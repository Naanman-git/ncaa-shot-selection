"""Plotly figures built only from observed shot locations and frozen estimates."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

NAVY = "#172b3a"
TEAL = "#167d8d"
ORANGE = "#c36333"
PAPER = "#fcfaf5"
MUTED = "#62717a"
ZONE_NAMES = {"rim": "At the rim", "paint": "Paint", "mid": "Midrange", "corner3": "Corner three", "abovebreak3": "Above-break three"}


def style_figure(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        template="plotly_white", height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": NAVY, "size": 12},
        margin={"l": 18, "r": 18, "t": 18, "b": 35},
        legend={"orientation": "h", "y": 1.13, "x": 0},
    )
    return fig


def court_bins(df: pd.DataFrame, cell_size: float = 3.0) -> dict:
    """Deterministic bins include every visible attempt, with no interpolation."""
    xedges = np.linspace(-25, 25, int(np.ceil(50 / cell_size)) + 1)
    yedges = np.linspace(-5.25, 41.75, int(np.ceil(47 / cell_size)) + 1)
    valid = df["shot_x"].between(-25, 25) & df["shot_y"].between(-5.25, 41.75)
    visible = df.loc[valid]
    positions = (visible["shot_x"].to_numpy(), visible["shot_y"].to_numpy())
    count = np.histogram2d(*positions, bins=(xedges, yedges))[0].T
    model = visible["model_p"].to_numpy(dtype=float)
    probability_sum = np.histogram2d(*positions, bins=(xedges, yedges), weights=model)[0].T
    points_sum = np.histogram2d(*positions, bins=(xedges, yedges), weights=model * visible["point_value"].to_numpy())[0].T
    probability = np.divide(probability_sum, count, out=np.full_like(count, np.nan), where=count > 0)
    points = np.divide(points_sum, count, out=np.full_like(count, np.nan), where=count > 0)
    return {"x": (xedges[1:] + xedges[:-1]) / 2, "y": (yedges[1:] + yedges[:-1]) / 2,
            "count": count, "probability": probability, "points": points,
            "visible": int(valid.sum()), "outside": int((~valid).sum())}


def _add_court(fig: go.Figure) -> None:
    def line(x, y):
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line={"color": "#78838a", "width": 1}, hoverinfo="skip", showlegend=False))
    line([-25, -25, 25, 25, -25], [41.75, -5.25, -5.25, 41.75, 41.75])
    line([-6, -6, 6, 6], [-5.25, 13.75, 13.75, -5.25])
    line([-3, 3], [-1.25, -1.25])
    theta = np.linspace(0, 2 * np.pi, 120)
    line(.75 * np.cos(theta), .75 * np.sin(theta))
    line(6 * np.cos(theta), 13.75 + 6 * np.sin(theta))
    r, corner = 22.1458, 21.65625
    angle = np.arccos(corner / r)
    arc = np.linspace(angle, np.pi - angle, 150)
    line(r * np.cos(arc), r * np.sin(arc))
    join = float(np.sqrt(r * r - corner * corner))
    line([-corner, -corner], [-5.25, join])
    line([corner, corner], [-5.25, join])


def court_heatmap(bins: dict, kind: str, minimum: int = 5) -> go.Figure:
    """Mask unsupported cells; model maps show average predictions at real shots."""
    if kind not in {"count", "probability", "points"}:
        raise ValueError("Unknown court-map quantity")
    z = np.array(bins[kind], copy=True, dtype=float)
    z[bins["count"] < (1 if kind == "count" else minimum)] = np.nan
    # Anchor the top of the complete legend below the plot. The default middle
    # anchor lets a horizontal colorbar overlap the baseline as the chart resizes.
    colorbar = {"orientation": "h", "x": .5, "xanchor": "center",
                "y": -.08, "yanchor": "top", "len": .86, "thickness": 12,
                "outlinewidth": 0, "xpad": 0, "ypad": 0,
                "tickfont": {"size": 11}, "nticks": 4}
    spec = {"count": ("Attempts", None, None, ".0f"), "probability": ("Make probability", 0, 1, ".0%"), "points": ("Points / attempt", 0, 2, ".2f")}[kind]
    colorbar["title"] = {"text": spec[0], "font": {"size": 11}, "side": "bottom"}
    colorbar["tickformat"] = spec[3]
    fig = go.Figure(go.Heatmap(x=bins["x"], y=bins["y"], z=z, customdata=bins["count"],
        zmin=spec[1], zmax=spec[2], colorscale=[[0, "#edf2ec"], [.45, "#73bbc0"], [1, "#116371"]],
        colorbar=colorbar, hoverongaps=False,
        hovertemplate=f"{spec[0]}: %{{z:{spec[3]}}}<br>Attempts in cell: %{{customdata:.0f}}<extra></extra>"))
    _add_court(fig)
    style_figure(fig, 410)
    fig.update_layout(margin={"l": 16, "r": 16, "t": 8, "b": 100})
    fig.update_xaxes(range=[-26, 26], visible=False, fixedrange=True, constrain="domain")
    fig.update_yaxes(range=[-6.25, 42.75], visible=False, fixedrange=True,
                     scaleanchor="x", scaleratio=1, constrain="domain")
    return fig


def mix_figure(table: pd.DataFrame) -> go.Figure:
    names = table["zone"].map(ZONE_NAMES).fillna(table["zone"])
    fig = go.Figure()
    for key, name, color in [("current_share", "Recorded mix", NAVY), ("recommended_share", "Scenario mix", TEAL)]:
        fig.add_trace(go.Bar(y=names, x=table[key], name=name, orientation="h", marker_color=color,
            hovertemplate="%{y}: %{x:.1%}<extra>" + name + "</extra>"))
    style_figure(fig, 350)
    fig.update_layout(barmode="group", margin={"l": 0, "r": 25, "t": 45, "b": 30})
    fig.update_xaxes(tickformat=".0%", title="Share of field-goal attempts", rangemode="tozero")
    fig.update_yaxes(autorange="reversed")
    return fig


def calibration_figure(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line={"color": "#a6adb0", "dash": "dash"}, name="Perfect calibration", hoverinfo="skip"))
    if len(frame):
        fig.add_trace(go.Scatter(x=frame["mean_predicted"], y=frame["observed"], mode="lines+markers", name="Selected model",
            line={"color": TEAL, "width": 3}, marker={"size": 9}, customdata=frame["n"],
            hovertemplate="Predicted: %{x:.1%}<br>Observed: %{y:.1%}<br>Attempts: %{customdata:,}<extra></extra>"))
    style_figure(fig, 370)
    fig.update_layout(margin={"l": 30, "r": 25, "t": 45, "b": 40})
    fig.update_xaxes(title="Average predicted make probability", range=[0, 1], tickformat=".0%")
    fig.update_yaxes(title="Observed make rate", range=[0, 1], tickformat=".0%")
    return fig
