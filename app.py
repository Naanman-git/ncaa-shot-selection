"""NCAA Division I men's basketball research and portfolio explorer."""
from __future__ import annotations

from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import streamlit as st

from ncaa_shot_selection.charts import (
    ZONE_NAMES, calibration_figure, court_bins, court_heatmap, mix_figure,
)
from ncaa_shot_selection.product import (
    load_analysis, load_scored_data, run_scenario, scope_summary,
)
from ncaa_shot_selection.streamlit_compat import full_width_kwargs
from ncaa_shot_selection.guide import GuideContext, render_beginner_guide
from ncaa_shot_selection.explorer import (
    render_comparison, render_player, render_context,
    render_confidence, render_release,
)

st.set_page_config(page_title="CourtSense · NCAA shot selection", page_icon="🏀", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  .stApp { background: #fcfaf5; }
  .block-container { max-width: 1480px; padding-top: 2.25rem; padding-bottom: 3rem; }
  [data-testid="stSidebar"] { border-right: 1px solid #dedfd8; }
  [data-testid="stSidebar"] .block-container { padding-top: 2rem; }
  h1, h2, h3 { color: #172b3a; letter-spacing: -.03em; }
  h1 { font-family: Georgia, serif; font-size: 3.5rem !important; font-weight: 500 !important; padding-top: .2rem !important; }
  h2 { font-size: 1.55rem !important; }
  h3 { font-size: 1.12rem !important; }
  .eyebrow { color: #167d8d; font-size: .72rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; margin: .2rem 0 .35rem; }
  .lead { color: #596c75; font-size: 1.05rem; max-width: 790px; line-height: 1.65; margin-bottom: 1.5rem; }
  .masthead { display:flex; justify-content:space-between; align-items:center; padding-bottom: .8rem; border-bottom:1px solid #d8dedb; margin-bottom:1.8rem; color:#172b3a; }
  .brand { font-size:1.15rem; letter-spacing:-.02em; font-weight:750; }
  .brand i { color:#c36333; font-style:normal; }
  .edition { font-size:.75rem; color:#65737a; }
  .scope-line { color:#64727a; font-size:.88rem; margin-top:-.5rem; margin-bottom:1.2rem; }
  .note { border-left: 3px solid #167d8d; padding: .65rem 1rem; color:#4c646d; background:#edf3ef; border-radius:0 5px 5px 0; line-height:1.55; margin:.7rem 0 1.3rem; font-size:.9rem; }
  [data-testid="stMetric"] { background:#f1f1e9; border:1px solid #e2e4da; border-radius:7px; padding:.9rem 1rem; }
  [data-testid="stMetricValue"] { font-size:1.85rem; color:#172b3a; }
  [data-testid="stMetricLabel"] { color:#60717a; font-size:.78rem; }
  .stTabs [data-baseweb="tab-list"] { border-bottom:1px solid #d8dedb; gap:1.3rem; margin:1.2rem 0; }
  .stTabs [data-baseweb="tab"] { font-size:.87rem; }
  .footer { border-top:1px solid #d8dedb; padding-top:1rem; margin-top:2.3rem; color:#758188; font-size:.76rem; }
  @media(max-width:700px) { h1 {font-size:2.4rem !important;} .edition{display:none;} .block-container{padding:1.2rem 1rem;} }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading the research snapshot…")
def analysis_data():
    return load_analysis(), load_scored_data()


@st.cache_data(show_spinner=False, max_entries=20)
def scenario_data(df: pd.DataFrame, max_shift: float, budget: float, three_cap: float, risk: float):
    return run_scenario(df, max_shift=max_shift, budget=budget, three_cap=three_cap, risk=risk, seed=42)


def csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")


def plotly_chart(figure, *, key: str | None = None):
    """Render a Plotly figure across Streamlit's width API transition.

    Some older Streamlit installations expose only ``use_container_width``;
    newer installations expose ``width="stretch"``. Passing an unsupported
    argument through the legacy ``**kwargs`` path produces the yellow warning
    shown in the app. Inspecting the installed function keeps the project
    runnable in VS Code environments with either API.
    """
    kwargs = {"config": {"displayModeBar": False}}
    kwargs.update(full_width_kwargs(st.plotly_chart))
    if key is not None:
        kwargs["key"] = key
    return st.plotly_chart(figure, **kwargs)


def dataframe(frame: pd.DataFrame, *, hide_index: bool = True, column_config=None):
    """Render a dataframe with the same compatibility behavior as charts."""
    kwargs = {"hide_index": hide_index}
    if column_config is not None:
        kwargs["column_config"] = column_config
    kwargs.update(full_width_kwargs(st.dataframe))
    return st.dataframe(frame, **kwargs)


def download_button(label: str, data, *, file_name: str, mime: str):
    """Render a full-width download button on old and new Streamlit builds."""
    kwargs = {"file_name": file_name, "mime": mime}
    kwargs.update(full_width_kwargs(st.download_button))
    return st.download_button(label, data, **kwargs)


def season_label(year: int) -> str:
    return f"{year - 1}–{str(year)[-2:]}"


def nice_model(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").capitalize()


def render_validation(results: dict):
    st.subheader("Check the model before using the answer")
    st.write("Probabilities are useful when their confidence agrees with what happened in later games. These are the saved evaluation results for the full eligible dataset; the team filter does not change them.")
    comparison = pd.DataFrame(results.get("model_comparison", []))
    calibration = pd.DataFrame(results.get("calibration", []))
    if comparison.empty:
        st.info("Model validation results will appear after the analysis build completes.")
        return
    seasons = sorted(comparison["season"].unique().tolist(), reverse=True)
    validation_season = st.selectbox("Evaluation season", seasons, format_func=season_label, key="validation_season")
    evaluation = comparison.loc[comparison["season"] == validation_season].copy()
    selected_name = results.get("selected_model", "")
    selected = evaluation.loc[evaluation["model"] == selected_name]
    chosen = selected.iloc[0] if len(selected) else evaluation.iloc[0]
    a, b, c = st.columns(3)
    a.metric(
        "Mean Brier score · lower is better",
        f"{chosen['brier']:.4f}",
        help="The average squared gap between each predicted make probability and the actual made-or-missed result.",
    )
    b.metric(
        "Mean log loss · lower is better",
        f"{chosen['log_loss']:.4f}",
        help="The average probability penalty for the actual result. Confident wrong predictions receive a larger penalty.",
    )
    c.metric("Evaluated attempts", f"{int(chosen['n']):,}")
    baseline = evaluation.loc[evaluation["model"] == "Global rate"]
    baseline_row = baseline.iloc[0] if len(baseline) else None
    brier_detail, log_loss_detail = st.columns(2, gap="large")
    with brier_detail:
        st.markdown("#### What the Brier score means")
        st.write(
            f"**{chosen['brier']:.4f}** is the mean squared difference between the model's "
            "predicted make probability and the actual result for every evaluated shot. "
            "A perfect score is 0; smaller values mean the probabilities were closer to what happened."
        )
        if baseline_row is not None:
            st.caption(
                f"The selected model is {baseline_row['brier'] - chosen['brier']:.4f} lower than "
                "the global-rate baseline on this evaluation season."
            )
    with log_loss_detail:
        st.markdown("#### What the log loss means")
        st.write(
            f"**{chosen['log_loss']:.4f}** is the mean penalty assigned to the probability given to "
            "the result that actually occurred. A perfect score is 0; smaller values are better, and "
            "confident wrong predictions are penalized much more heavily."
        )
        if baseline_row is not None:
            st.caption(
                f"The selected model is {baseline_row['log_loss'] - chosen['log_loss']:.4f} lower than "
                "the global-rate baseline on this evaluation season."
            )
    st.caption(
        "Both values are averages across the evaluated attempts. They are model-error scores, not shooting percentages, "
        "and should be compared using the same shots and season."
    )
    chart, explanation = st.columns([1.15, 1], gap="large")
    with chart:
        st.markdown("### Probability calibration")
        cal = calibration.loc[calibration["season"] == validation_season] if "season" in calibration else calibration
        if not cal.empty:
            plotly_chart(calibration_figure(cal))
        else:
            st.info("No calibration bins available for this season.")
    with explanation:
        st.markdown("### How to read this")
        st.write("A point close to the diagonal means predicted and observed make rates agree. A point below the line means the model was too optimistic in that probability range.")
        st.write(f"**Selected model:** {nice_model(str(selected_name))}.")
        st.write("The simple baselines are the standard the selected model must earn its place against. The separate score explanations above describe what each average measures.")
        st.caption("2022–23 and 2023–24 provide training data; 2024–25 selects the model; 2025–26 is the fixed final evaluation. The saved report documents the freeze and evaluation policy.")
    table = evaluation.rename(columns={"model": "Model", "n": "Attempts", "brier": "Brier score", "log_loss": "Log loss"})
    dataframe(table[["Model", "Attempts", "Brier score", "Log loss"]], column_config={"Brier score": st.column_config.NumberColumn(format="%.4f"), "Log loss": st.column_config.NumberColumn(format="%.4f")})
    hypotheses = pd.DataFrame(results.get("hypothesis_results", []))
    if not hypotheses.empty:
        st.markdown("### Prespecified hypotheses")
        view = hypotheses.rename(columns={"id": "ID", "hypothesis": "Hypothesis", "result": "Held-out result", "status": "Status"})
        dataframe(view[["ID", "Hypothesis", "Held-out result", "Status"]])
    interpretation = pd.DataFrame(results.get("model_interpretation", []))
    if not interpretation.empty:
        with st.expander("Model coefficient interpretation"):
            st.write("The distance effect uses a nonlinear spline, so the report interprets it through held-out distance bands. These standardized terms are associations with prediction odds, holding the other transformed inputs fixed.")
            view = interpretation.rename(columns={"feature": "Feature", "coefficient": "Coefficient", "odds_multiplier": "Odds multiplier", "interpretation": "Interpretation"})
            dataframe(view[["Feature", "Coefficient", "Odds multiplier", "Interpretation"]], column_config={"Coefficient": st.column_config.NumberColumn(format="%.3f"), "Odds multiplier": st.column_config.NumberColumn(format="%.3f")})


def render_methods(results: dict):
    st.subheader("The evidence behind the explorer")
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("### What this project answers")
        st.write("For recorded NCAA Division I men's field-goal attempts, where are make probability and expected points higher, and how do modest changes in the shot mix affect estimated scoring?")
        st.write("One row represents a recorded field-goal attempt. Expected points equal the predicted make probability multiplied by the attempt's source-reported point value. Free throws and the value of passing are outside this outcome.")
        st.markdown("### Data and reproducibility")
        st.write("The NCAA-native shot files are distributed by SportsDataverse. The build preserves raw files, checks duplicates and coordinates, validates Division I membership, and records exclusions. Coverage is conditional on the publisher's available games.")
        st.markdown("[NCAA shot data](https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/ncaa_mbb_shots) · [NCAA rules and court resources](https://www.ncaa.org/sports/2013/12/2/men-s-basketball-rules-of-the-game.aspx)")
        st.markdown("### Coding guide")
        st.write("A project coding guide defines the historical fields, five source zones, inclusion rules, anonymous prospective fields, quality checks, and missing-data policy.")
    with b:
        st.markdown("### Interpreting a scenario")
        st.write("The scenario redistributes a small share of recorded attempts between five source-defined zones. Zone estimates use the selected sample with a pooled prior; the frozen predictive model and the retrospective scenario answer different questions.")
        st.write("An estimated gain assumes shooting efficiency stays similar after the mix changes. Defenders, fatigue, play calls, shot availability, and roster changes can all break that assumption. Uncertainty describes the estimate under the model assumptions, not every source of real-world uncertainty.")
        st.write("The court shows approximately three-foot cells. Prediction maps average frozen model estimates only at observed locations. Low-count cells are blank. The source zones are not inferred from the displayed court lines.")
        st.markdown("### Prospective validation")
        st.write("The project includes a post-freeze protocol, anonymous shot template, and analyzer for new attempts. The analyzer will report Brier score, log loss, calibration, strategy points per attempt, and a session-cluster interval after real observations are collected.")
        st.caption("No prospective outcome is reported yet. The historical scenario remains a conditional estimate rather than an intervention result.")
    limitations = results.get("limitations", [])
    if limitations:
        with st.expander("Study limitations", expanded=True):
            if isinstance(limitations, list):
                for item in limitations:
                    st.write(f"• {item}")
            else:
                st.write(limitations)
    with st.expander("Audit and run details"):
        st.json({"run_id": results.get("run_id", "unavailable"), "audit": results.get("audit", {})}, expanded=False)
    st.markdown("### Take the research with you")
    downloads = st.columns(5)
    with downloads[0]:
        download_button("Download analysis results", json.dumps(results, indent=2, default=str), file_name="ncaa_analysis_results.json", mime="application/json")
    candidates = [(ROOT / "output/pdf", ".pdf", "application/pdf"), (ROOT / "output/presentation", ".pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation")]
    for col, (directory, suffix, mime) in zip(downloads[1:3], candidates):
        files = sorted(directory.glob(f"*{suffix}")) if directory.exists() else []
        if files:
            artifact = files[-1]
            with col:
                download_button("Download research report" if suffix == ".pdf" else "Download presentation", artifact.read_bytes(), file_name=artifact.name, mime=mime)
        else:
            col.caption("Research report pending" if suffix == ".pdf" else "Presentation pending")
    protocol = ROOT / "docs/PROSPECTIVE_VALIDATION_PROTOCOL.md"
    template = ROOT / "data/templates/prospective_shots_template.csv"
    if protocol.exists():
        with downloads[3]:
            download_button("Download validation protocol", protocol.read_text(), file_name=protocol.name, mime="text/markdown")
    if template.exists():
        with downloads[4]:
            download_button("Download shot template", template.read_bytes(), file_name=template.name, mime="text/csv")


def main():
    st.markdown('<div class="masthead"><div class="brand"><i>◉</i> CourtSense</div><div class="edition">COLLEGE BASKETBALL / RESEARCH EXPLORER</div></div>', unsafe_allow_html=True)
    try:
        results, shots = analysis_data()
    except (FileNotFoundError, ValueError, KeyError) as exc:
        st.title("The court is getting ready.")
        st.info("The explorer needs the completed research snapshot. Run the project's analysis build, then reload this page.")
        with st.expander("Build details"):
            st.code(str(exc))
        st.stop()
    if shots.empty:
        st.warning("The research snapshot has no eligible shots. Review the data audit before continuing.")
        st.stop()
    with st.sidebar:
        st.markdown('<p class="eyebrow">Explore the evidence</p>', unsafe_allow_html=True)
        st.header("Explore & learn")
        st.caption("Use the arrow above to close this sidebar; the top-left arrow opens it again.")
        filters_tab, guide_tab = st.tabs(["Choose your view", "Beginner’s guide"])
        with filters_tab:
            seasons = sorted(shots["season"].unique().tolist(), reverse=True)
            season = st.selectbox("Season", seasons, format_func=season_label, key="season")
            season_shots = shots.loc[shots["season"] == season]
            teams = sorted(season_shots["team_name"].dropna().unique().tolist())
            default_team = next((name for name in teams if "Ohio State" in name), None)
            team_options = ["All Division I teams", *teams]
            if st.session_state.get("team", team_options[0]) not in team_options:
                st.session_state["team"] = team_options[0]
            team = st.selectbox("Team", team_options, index=team_options.index(default_team) if default_team else 0, key="team")
            team_shots = season_shots if team == team_options[0] else season_shots.loc[season_shots["team_name"] == team]
            player_table = team_shots[["player_key", "player_name"]].drop_duplicates("player_key").sort_values("player_name")
            player_names = dict(zip(player_table["player_key"], player_table["player_name"]))
            if st.session_state.get("player", "all") not in ["all", *player_names]:
                st.session_state["player"] = "all"
            player = st.selectbox("Player", ["all", *player_table["player_key"].tolist()], format_func=lambda key: "All players" if key == "all" else str(player_names.get(key, key)), key="player")
            scope = team_shots if player == "all" else team_shots.loc[team_shots["player_key"] == player]
            st.divider()
            cell_minimum = st.slider("Minimum attempts per model-map cell", 1, 30, 5, help="Only the probability and expected-points maps hide cells below this threshold. The frequency map retains all visible attempts.")
            st.caption("Source seasons use the ending year. This explorer covers men's Division I basketball only.")
            st.markdown('<div class="note">A shot-quality estimate is evidence for a question, not a guarantee of a better play.</div>', unsafe_allow_html=True)
    st.markdown('<p class="eyebrow">NCAA DIVISION I · MEN’S BASKETBALL</p>', unsafe_allow_html=True)
    st.title("Find the value in every zone.")
    st.markdown('<p class="lead">Explore where teams shoot, how likely those attempts are to fall, and what a carefully constrained change in shot mix could mean.</p>', unsafe_allow_html=True)
    label = team if player == "all" else f"{player_names[player]} · {team}"
    st.markdown(f'<p class="scope-line">{escape(label)} &nbsp; / &nbsp; {season_label(season)}</p>', unsafe_allow_html=True)
    if scope.empty:
        st.info("No attempts match this selection. Choose another team or player.")
        st.stop()
    summary = scope_summary(scope)
    scenario = {}
    cards = st.columns(5)
    cards[0].metric("Recorded attempts", f"{summary['count']:,}", help=f"Across {summary['games']:,} distinct games in the available source.")
    cards[1].metric("Games represented", f"{summary['games']:,}")
    cards[2].metric("Observed field-goal %", f"{summary['fg_pct']:.1%}", help="Shots made divided by shots attempted. Making 45 of 100 shots gives 45%. Free throws are excluded.")
    cards[3].metric("Observed points / attempt", f"{summary['observed_pps']:.3f}", help="Actual field-goal points divided by attempts. 110 points from 100 attempts equals 1.10 points per attempt.")
    cards[4].metric("Predicted points / attempt", f"{summary['expected_pps']:.3f}", help="Average predicted make probability multiplied by each shot's point value. A 40% chance on a three-pointer gives 1.20 expected points.")
    st.caption("First visit? Open the sidebar using the top-left arrow and select Beginner’s guide for a tour or a term lookup.")
    if summary["count"] < 100:
        st.warning("Small sample: fewer than 100 recorded attempts. Treat maps and zone estimates as exploratory; a few shots can change them substantially.")
    court_tab, scenario_tab, compare_tab, player_tab, context_tab, validation_tab, methods_tab = st.tabs([
        "Court explorer", "Shot-mix scenarios", "Compare teams", "Player development",
        "Team context", "Model validation", "Methods & downloads",
    ])
    with court_tab:
        st.subheader("One court. Three ways to read it.")
        st.caption("Every cell is grounded in recorded attempts. Hover for the cell's count; empty cells have no eligible support.")
        bins = court_bins(scope)
        columns = st.columns(3, gap="medium")
        for column, kind, title, subtitle in zip(columns, ["count", "probability", "points"], ["01 / Where shots happen", "02 / How often they fall", "03 / What they are worth"], ["Recorded attempt frequency", "Average predicted make probability", "Average predicted points per attempt"]):
            with column:
                st.markdown(f"### {title}")
                st.caption(subtitle)
                plotly_chart(court_heatmap(bins, kind, cell_minimum), key=f"court_{kind}")
        st.caption(f"{bins['visible']:,} attempts within the displayed half-court. {bins['outside']:,} attempts outside this view remain in totals and analysis. Probability maps require at least {cell_minimum} attempts per cell.")
        st.markdown("### The zone breakdown")
        zone_table = summary["zone_table"].copy()
        if "zone" in zone_table:
            zone_table["zone"] = zone_table["zone"].map(ZONE_NAMES).fillna(zone_table["zone"])
        elif "shot_zone" in zone_table:
            zone_table["shot_zone"] = zone_table["shot_zone"].map(ZONE_NAMES).fillna(zone_table["shot_zone"])
        dataframe(zone_table, column_config={
            "shot_zone": "Court zone", "zone": "Court zone",
            "count": st.column_config.NumberColumn("Attempts", format="%,d"),
            "makes": st.column_config.NumberColumn("Shots made", format="%,d"),
            "fg_pct": st.column_config.NumberColumn("Field-goal %", format="percent", help="Makes divided by attempts; free throws excluded."),
            "observed_pps": st.column_config.NumberColumn("Observed points / attempt", format="%.3f"),
            "expected_pps": st.column_config.NumberColumn("Predicted points / attempt", format="%.3f"),
            "share": st.column_config.NumberColumn("Share of attempts", format="percent"),
        })
        download_button("Download selected zone summary", csv_bytes(zone_table), file_name=f"ncaa_{season}_zone_summary.csv", mime="text/csv")
    with scenario_tab:
        st.subheader("Change the mix. Keep the assumptions visible.")
        st.write("Explore modest changes in the selected sample's zone shares. The estimates below use observed zone results with shrinkage and uncertainty; they are retrospective scenarios.")
        if summary["count"] < 100:
            st.info("At least 100 attempts are required for a shot-mix scenario. Broaden the selection to a team or all players.")
        else:
            control1, control2, control3, control4 = st.columns(4)
            max_shift = control1.slider("Maximum shift per zone", 0, 15, 5, 1, format="%d pp", help="The maximum percentage-point increase or decrease in one zone's share.") / 100
            budget = control2.slider("Total mix movement", 0, 40, 20, 2, format="%d pp", help="Sum of absolute changes across zones. Moving 5 percentage points from one zone to another uses 10 points of movement.") / 100
            three_cap = control3.slider("Three-point share cap", 20, 100, 60, 5, format="%d%%") / 100
            risk = control4.slider("Uncertainty penalty", 0.0, 2.0, 1.0, .25, help="Higher values favor zones with more certain expected-point estimates. This is a sensitivity control, not a confidence level.")
            scenario = scenario_data(scope, max_shift, budget, three_cap, risk)
            if not scenario.get("feasible", False):
                st.warning(scenario.get("message", "These constraints are infeasible. Increase the three-point cap or allow more movement."))
            else:
                x, y, z = st.columns(3)
                x.metric("Current mix · estimated pts / attempt", f"{scenario['current_ep']:.3f}")
                y.metric("Scenario mix · estimated pts / attempt", f"{scenario['recommended_ep']:.3f}")
                z.metric("Estimated change / 100 attempts", f"{scenario['gain_per100']:+.1f}")
                st.markdown(f'<div class="note">Conditional 95% interval for the change: <b>{scenario["gain_low"]:+.1f} to {scenario["gain_high"]:+.1f} points per 100 attempts</b>. This assumes the estimated zone efficiencies persist after the mix changes. It does not establish a causal improvement.</div>', unsafe_allow_html=True)
                left, right = st.columns([1.1, 1], gap="large")
                with left:
                    plotly_chart(mix_figure(scenario["table"]))
                with right:
                    st.markdown("### Read the recommendation")
                    deltas = scenario["table"].assign(change=lambda t: t.recommended_share - t.current_share)
                    changed = deltas.loc[deltas.change.abs() >= .001].sort_values("change", ascending=False)
                    if changed.empty:
                        st.write("The constraints and evidence support retaining the current mix.")
                    else:
                        for row in changed.itertuples():
                            verb = "Increase" if row.change > 0 else "Reduce"
                            st.write(f"{verb} **{ZONE_NAMES.get(row.zone, row.zone).lower()}** by **{abs(row.change) * 100:.1f} percentage points**.")
                    st.caption("Zones with insufficient evidence are kept near their recorded shares. Availability of new shot opportunities is not observed.")
                    if scenario.get("message"):
                        st.caption(scenario["message"])
                with st.expander("Zone estimates and scenario table"):
                    scenario_view = scenario["table"].copy()
                    scenario_view["zone"] = scenario_view["zone"].map(ZONE_NAMES).fillna(scenario_view["zone"])
                    dataframe(scenario_view, column_config={
                        "zone": "Court zone",
                        "count": st.column_config.NumberColumn("Attempts", format="%,d"),
                        "makes": st.column_config.NumberColumn("Shots made", format="%,d"),
                        "raw_fg": st.column_config.NumberColumn("Recorded make rate", format="percent"),
                        "shrunk_fg": st.column_config.NumberColumn("Adjusted make rate", format="percent", help="Recorded rate blended with an earlier pooled rate to stabilize small samples."),
                        "current_share": st.column_config.NumberColumn("Recorded shot share", format="percent"),
                        "recommended_share": st.column_config.NumberColumn("Scenario shot share", format="percent"),
                        "ep": st.column_config.NumberColumn("Estimated points / attempt", format="%.3f"),
                        "ep_low": st.column_config.NumberColumn("Lower 95% bound", format="%.3f", help="Lower game-resampling bound for estimated points per attempt."),
                        "ep_high": st.column_config.NumberColumn("Upper 95% bound", format="%.3f", help="Upper game-resampling bound for estimated points per attempt."),
                        "eligible": st.column_config.CheckboxColumn("Enough evidence to change mix"),
                    })
                download_button("Download scenario table", csv_bytes(scenario["table"]), file_name=f"ncaa_{season}_scenario.csv", mime="text/csv")
            history = shots if team == "All Division I teams" else shots.loc[shots.team_name == team]
            if player != "all":
                history = scope
            render_confidence(scope, history, scenario)
    with compare_tab:
        render_comparison(shots, season, team, results)
    with player_tab:
        profile = render_player(shots, season, team, player)
    with context_tab:
        team_totals = render_context(season, team)
    with validation_tab:
        render_validation(results)
    with methods_tab:
        render_methods(results)
        render_release(results)
    evaluation = next((row for row in results.get("model_comparison", [])
                       if row["model"] == results.get("selected_model")
                       and row["season"] == st.session_state.get("validation_season")), {})
    with guide_tab:
        render_beginner_guide(st, GuideContext(
            label=label, season=season, summary=summary, evaluation=evaluation,
            scenario=scenario, minimum=cell_minimum,
            visible=bins["visible"], outside=bins["outside"],
            mean_probability=float(scope["model_p"].mean()),
            team_label=team, team_totals=team_totals or {},
            profile_label=profile[0] if profile else "No profile available",
            profile_summary=profile[1] if profile else {},
        ))
    st.markdown(f'<div class="footer">CourtSense · NCAA men’s basketball research · Run {escape(str(results.get("run_id", "unavailable")))} · Academic study & portfolio explorer</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
