"""Shared data contract used by analysis, dashboard and documents."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .modeling import ZONES
from .optimization import solve_mix

ROOT = Path(__file__).resolve().parents[2]
APP_DATA = ROOT / "data" / "app"


def _artifact_path(name: str, fallback: Path) -> Path:
    """Prefer the small, tracked deployment snapshot when it exists."""
    candidate = APP_DATA / name
    return candidate if candidate.exists() else fallback


def load_analysis():
    path = _artifact_path("final_results.json", ROOT / "data" / "outputs" / "final_results.json")
    return json.loads(path.read_text())


def load_scored_data():
    path = _artifact_path("shots_scored.parquet", ROOT / "data" / "processed" / "shots_scored.parquet")
    return pd.read_parquet(path)


def scope_summary(df):
    if df.empty:
        return {"count": 0, "games": 0, "fg_pct": 0., "observed_pps": 0.,
                "expected_pps": 0., "zone_table": pd.DataFrame()}
    work = df.assign(observed_points=df.made*df.point_value,
                     expected_points=df.model_p*df.point_value)
    table = work.groupby("shot_zone", observed=True).agg(
        count=("made", "size"), makes=("made", "sum"), fg_pct=("made", "mean"),
        observed_pps=("observed_points", "mean"), expected_pps=("expected_points", "mean"))
    table["share"] = table["count"]/len(df)
    return {"count": len(df), "games": int(df.contest_id.nunique()),
            "fg_pct": float(df.made.mean()), "observed_pps": float(work.observed_points.mean()),
            "expected_pps": float(work.expected_points.mean()), "zone_table": table.reset_index()}


def run_scenario(df, max_shift=.05, budget=.20, three_cap=.60, risk=1., seed=42,
                 *, prior_rates=None, repeats=500):
    if risk < 0 or not np.isfinite(risk):
        raise ValueError("Risk penalty must be finite and nonnegative")
    empty = {"table": pd.DataFrame(), "current_ep": 0., "recommended_ep": 0.,
             "gain_per100": 0., "gain_low": 0., "gain_high": 0., "feasible": False,
             "message": "Select at least 80 attempts across five games."}
    if len(df)<80 or df.contest_id.nunique()<5:
        return empty
    if prior_rates is None:
        prior_rates = load_analysis()["zone_prior"]
    counts = df.groupby("shot_zone", observed=True).made.agg(["sum", "count"]).reindex(ZONES, fill_value=0)
    current = counts["count"].to_numpy(float)/len(df)
    prior = np.array([prior_rates[z] for z in ZONES])
    values = np.array([2.,2.,2.,3.,3.])
    ep = (counts["sum"].to_numpy()+30*prior)/(counts["count"].to_numpy()+30)*values
    games = df.groupby(["contest_id", "shot_zone"], observed=True).made.agg(["sum", "count"])
    n = games["count"].unstack(fill_value=0).reindex(columns=ZONES, fill_value=0).to_numpy(float)
    m = games["sum"].unstack(fill_value=0).reindex(columns=ZONES, fill_value=0).to_numpy(float)
    rng = np.random.default_rng(seed)
    samples = np.empty((repeats,5))
    for i in range(repeats):
        picks = rng.integers(0,len(n),len(n))
        samples[i] = (m[picks].sum(axis=0)+30*prior)/(n[picks].sum(axis=0)+30)*values
    eligible = (counts["count"].to_numpy()>=30)&((n>0).sum(axis=0)>=5)
    solved = solve_mix(current, ep-risk*samples.std(axis=0,ddof=1), eligible,
                       max_shift=max_shift, budget=budget, three_cap=three_cap)
    q = solved["share"]
    gains = 100*samples@(q-current)
    lo, hi = np.quantile(gains,[.025,.975])
    table = pd.DataFrame({"zone": ZONES, "count": counts["count"].to_numpy(),
        "current_share": current, "recommended_share": q, "ep": ep,
        "ep_low": np.quantile(samples,.025,axis=0),
        "ep_high": np.quantile(samples,.975,axis=0), "eligible": eligible})
    return {"table": table, "current_ep": float(current@ep),
        "recommended_ep": float(q@ep), "gain_per100": float(100*(q-current)@ep),
        "gain_low": float(lo), "gain_high": float(hi), "feasible": solved["feasible"],
        "message": solved["message"], "bootstrap_repeats": repeats,
        "interpretation": "Descriptive, conditional on unchanged zone accuracy. The fixed-mix game-bootstrap range does not account for optimization selection, opponent response, or causal effects."}
