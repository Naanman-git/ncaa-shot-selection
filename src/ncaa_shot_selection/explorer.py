"""Comparison, player and context pages."""
from pathlib import Path
import re
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from .charts import ZONE_NAMES, style_figure, court_bins, court_heatmap
from .insights import APP_VERSION, game_trend, points_interval, report_card, zone_evidence
from .product import scope_summary, run_scenario

ROOT = Path(__file__).resolve().parents[2]


def show_table(frame):
    st.dataframe(frame, hide_index=True, width="stretch")


def chart(fig, key):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=key)


@st.cache_data(max_entries=40, show_spinner=False)
def default_scenario(frame, shift=.05):
    return run_scenario(frame, max_shift=shift, budget=.20, three_cap=.60, risk=1., seed=42)


def evidence_table(frame):
    t = zone_evidence(frame)
    if t.empty:
        return pd.DataFrame()
    return pd.DataFrame({"Zone": t.shot_zone.map(ZONE_NAMES), "Attempts": t["count"],
                         "Games": t.games, "Observed FG%": t.fg_pct.map(lambda x:f"{x:.1%}"),
                         "Observed pts / attempt": t.observed_pps.map(lambda x:f"{x:.3f}"),
                         "Predicted pts / attempt": t.expected_pps.map(lambda x:f"{x:.3f}"), "Sample support": t.support})


def render_confidence(scope, history, scenario):
    with st.expander("How much evidence supports this scenario?"):
        st.write("Sample support describes how much data we have. It is not the probability that a recommendation will work.")
        show_table(evidence_table(scope))
        st.caption("Usable: ≥30 attempts across ≥5 games. Broader: ≥100 attempts across ≥10 games. Anything smaller is limited. These are descriptive thresholds.")
        if scenario.get("feasible"):
            if abs(scenario["gain_per100"]) < .001:
                st.info("The selected scenario leaves the estimated scoring rate unchanged.")
            elif scenario["gain_low"] <= 0 <= scenario["gain_high"]:
                st.info("The conditional interval includes zero: these data do not clearly separate the estimated gain from no change.")
            else:
                st.write("The conditional interval excludes zero. This describes the fixed scenario under unchanged efficiencies; it still does not establish a causal improvement.")
        if st.button("Check stricter limits and season stability", key="check_stability"):
            rows=[]
            for shift in [.025,.05,.10]:
                r=default_scenario(scope, shift)
                rows.append({"Maximum shift per zone":f"{shift:.1%}", "Status":"Feasible" if r["feasible"] else "Infeasible",
                             "Estimated gain / 100":round(r["gain_per100"],2) if r["feasible"] else None})
            st.write("Sensitivity check: default movement budget, three-point cap and uncertainty penalty; only the zone limit changes.")
            show_table(pd.DataFrame(rows))
            rows=[]
            for season, f in history.groupby("season", observed=True):
                r=default_scenario(f)
                changes=r["table"]
                if r["feasible"] and not changes.empty:
                    delta=changes.recommended_share-changes.current_share
                    increases=", ".join(ZONE_NAMES[z] for z in changes.loc[delta>.001,"zone"]) or "No increase"
                    rows.append({"Season":f"{season-1}–{str(season)[-2:]}","Attempts":len(f),"Zones with increased share":increases,
                                 "Conditional gain / 100":round(r["gain_per100"],2)})
            if rows:
                st.write("Historical scenario stability: each season is analyzed separately. Different rosters and schedules can change the result; this is not a new model evaluation.")
                show_table(pd.DataFrame(rows))
            else:
                st.info("No seasons have enough support for this comparison.")


def render_comparison(shots, season, current_team, results):
    st.subheader("Two teams. The same questions.")
    st.caption("Uses whole teams in the selected season. The sidebar's player selection does not restrict this comparison. Differences are descriptive, not adjusted for opponents.")
    data=shots.loc[shots.season==season]
    teams=sorted(data.team_name.unique())
    if len(teams)<2:
        st.info("Two teams are needed for a comparison."); return
    left,right=st.columns(2)
    if st.session_state.get("compare_a", teams[0]) not in teams:
        st.session_state["compare_a"] = teams[0]
    team_a=left.selectbox("First team", teams, index=teams.index(current_team) if current_team in teams else 0, key="compare_a")
    other=[t for t in teams if t!=team_a]
    if st.session_state.get("compare_b", other[0]) not in other:
        st.session_state["compare_b"] = other[0]
    team_b=right.selectbox("Second team", other, key="compare_b")
    frames=[data.loc[data.team_name==t] for t in [team_a,team_b]]
    summaries=[scope_summary(f) for f in frames]
    for col,team,f,s in zip([left,right],[team_a,team_b],frames,summaries):
        with col:
            st.markdown(f"### {team}")
            st.write(f"**{s['count']:,} attempts** · {s['games']} games · {s['fg_pct']:.1%} field-goal percentage")
            st.metric("Observed points / attempt",f"{s['observed_pps']:.3f}")
            st.metric("Predicted points / attempt",f"{s['expected_pps']:.3f}")
            ci=points_interval(f)
            if ci: st.caption(f"Observed rate · game-resampling 95% interval: {ci[0]:.3f}–{ci[1]:.3f}. Not adjusted for schedule.")
            r=default_scenario(f)
            if r["feasible"]:
                st.write(f"Default scenario opportunity: **{r['gain_per100']:+.1f} points / 100 attempts** (conditional interval {r['gain_low']:+.1f} to {r['gain_high']:+.1f}).")
            else: st.caption("A feasible default scenario is unavailable for this sample.")
            st.download_button("Download team report card",report_card(team,int(season),f,r,results),
                               file_name=f"courtsense_{int(season)}_{re.sub(r'[^a-z0-9]+', '_', team.lower()).strip('_')}_report.html",mime="text/html",key=f"report_{team}",width="stretch")
    st.caption("Report cards are self-contained HTML. Open the download in a browser, then Print → Save as PDF for a compact handout.")
    fig=go.Figure()
    for team,s in zip([team_a,team_b],summaries):
        t=s["zone_table"].set_index("shot_zone").reindex(ZONE_NAMES.keys())
        fig.add_bar(name=team,x=list(ZONE_NAMES.values()),y=t.share.fillna(0),hovertemplate="%{x}: %{y:.1%}<extra>%{fullData.name}</extra>")
    style_figure(fig,360);fig.update_layout(barmode="group",margin=dict(t=60,b=65));fig.update_yaxes(tickformat=".0%",title="Share of attempts")
    chart(fig,"compare_mix")
    st.write("**Where the evidence comes from**")
    for col,team,f in zip(st.columns(2),[team_a,team_b],frames):
        with col:
            st.caption(team);show_table(evidence_table(f))
    st.caption("Training-season predicted values (2022–23 and 2023–24) are in-sample descriptions, not held-out performance estimates.")


def render_player(shots, season, team, selected_player):
    st.subheader("A player's season, one game at a time")
    data=shots.loc[shots.season==season]
    if team!="All Division I teams": data=data.loc[data.team_name==team]
    options=data.groupby("player_key", observed=True).agg(name=("player_name","first"),team=("team_name","first"),attempts=("made","size")).sort_values("attempts",ascending=False)
    if options.empty: st.info("No players in this selection.");return
    ids=options.index.tolist()
    if st.session_state.get("profile_player", ids[0]) not in ids:
        st.session_state["profile_player"] = ids[0]
    player=st.selectbox("Player profile",ids,index=ids.index(selected_player) if selected_player in ids else 0,
        format_func=lambda k:f"{options.loc[k,'name']} · {options.loc[k,'team']}",key="profile_player")
    f=data.loc[data.player_key==player]
    s=scope_summary(f)
    st.write(f"**{options.loc[player,'name']}** · {s['count']:,} attempts across {s['games']} games")
    st.caption("Profiles use source IDs within one season. Most source IDs change between seasons, so we do not automatically merge players with similar names.")
    if s["count"]<100: st.warning("Small sample: fewer than 100 attempts. Treat trends and practice suggestions as exploratory.")
    trend=game_trend(f)
    fig=go.Figure()
    for col in ["Observed points / attempt","Predicted points / attempt","Recent 5 games · observed"]:
        fig.add_scatter(x=trend.game_date,y=trend[col],name=col,mode="lines+markers",customdata=trend.attempts,hovertemplate="%{x}<br>%{y:.3f} points/attempt<br>%{customdata} attempts in this game<extra>%{fullData.name}</extra>")
    style_figure(fig,370);fig.update_layout(margin=dict(t=75,b=40));chart(fig,"player_trend")
    st.caption("Recent 5 games uses total points divided by total attempts in that window. Early windows contain fewer than five games; low-volume games can still vary widely.")
    show_table(evidence_table(f))
    evidence=zone_evidence(f);usable=evidence[evidence.support!="Limited sample"]
    if not usable.empty:
        best=usable.loc[usable.observed_pps.idxmax()];review=usable.loc[usable.gap.idxmin()]
        st.write(f"**Observed strength:** {ZONE_NAMES[best.shot_zone]} has the highest observed points per attempt among zones with usable support.")
        st.write(f"**Practice / video-review prompt:** inspect {ZONE_NAMES[review.shot_zone].lower()} shots, where the observed-minus-predicted gap is {review.gap:+.3f} points per attempt. Review balance, shot preparation and defensive pressure before deciding on a drill.")
    else: st.info("There is not enough zone evidence to identify a supported practice priority.")
    st.caption("These prompts describe this sample, not a diagnosis of ability or a validated training prescription. Training-season model estimates are in-sample.")
    chart(court_heatmap(court_bins(f),"count"),"player_court")
    st.download_button("Download player game trend",trend.to_csv(index=False),file_name=f"player_{int(season)}_trend.csv",mime="text/csv")
    return f"{options.loc[player,'name']} · {options.loc[player,'team']}", s


@st.cache_data(show_spinner=False)
def load_context():
    p=ROOT/"data/app/team_context.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def render_context(season,team):
    st.subheader("Beyond the shot: the whole offense")
    st.write("This view adds free throws, turnovers and offensive rebounds using reconciled team box scores. Possessions are estimated from totals; individual possession sequences have not been reconstructed.")
    data=load_context()
    if data.empty:st.info("The context snapshot is unavailable. The shot explorer remains usable.");return
    data=data.loc[data.season==season]
    if team!="All Division I teams":data=data.loc[data.team_name==team]
    if data.empty:st.info("No reconciled box scores are available for this selection.");return
    totals=data.select_dtypes("number").sum()
    a,b,c=st.columns(3)
    a.metric("Points / estimated possession",f"{totals.points/totals.possessions:.3f}")
    b.metric("Free-throw points",f"{int(totals.free_throws):,}")
    c.metric("Turnovers / 100 estimated possessions",f"{100*totals.turnovers/totals.possessions:.1f}")
    st.caption(f"Based on {int(totals.games):,} team-games. Selecting all teams counts both teams in each game. Rates use ratios of totals and are not opponent-adjusted.")
    grouped=data.groupby("designation", observed=True).sum(numeric_only=True)
    view=pd.DataFrame({"Source designation":grouped.index,"Team-games":grouped.games,
        "Points / estimated possession":(grouped.points/grouped.possessions).round(3),
        "Free throws made":grouped.free_throws,"Offensive rebounds":grouped.offensive_rebounds,
        "Turnovers":grouped.turnovers}).reset_index(drop=True)
    show_table(view)
    st.caption("Source home/away designations can include neutral-site games. These descriptive splits do not establish a home-court effect.")
    with st.expander("How possessions are estimated and what remains unavailable"):
        st.write("For each team-game: field-goal attempts − offensive rebounds + total turnovers + 0.475 × free-throw attempts. Average the two teams' estimates for that game, then divide total points by total estimated possessions.")
        st.markdown("Method adapted from [Ken Pomeroy's ratings glossary](https://kenpom.com/blog/ratings-glossary/). Our aggregate rates use ratios of totals, without his schedule adjustments.")
        st.write("The data does not reliably attach defender distance, shot-clock pressure, fatigue or play type to the NCAA-native shot records. Game-final scores are outcomes, so they are not added as predictors of earlier shots. Exact second-chance possession sequences remain unavailable in this view.")
        st.markdown("Box-score source: [SportsDataverse / hoopR.mbb](https://github.com/sportsdataverse/hoopR-mbb-data), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). CourtSense joins, checks and aggregates these ESPN-origin records; no endorsement is implied.")
    st.download_button("Download selected team context",data.to_csv(index=False),file_name=f"team_context_{int(season)}.csv",mime="text/csv")
    return totals.to_dict()


def render_release(results):
    st.caption(f"App {APP_VERSION} · Analysis snapshot built {str(results.get('generated_utc','unknown'))[:10]} · Protocol {results.get('config',{}).get('protocol_version','1.0')} · This is a saved snapshot, not a live data feed.")
    with st.expander("Data versions, updates and feedback"):
        st.write(f"Frozen analysis run: {results.get('run_id')}")
        st.write("New data builds are validated in staging and reviewed before replacing the hosted snapshot. The research's original test-season results remain frozen.")
        st.markdown("[Repository and issue tracker — collaborators only](https://github.com/Naanman-git/ncaa-shot-selection/issues)")
        feedback=st.text_area("Describe a problem or suggestion",key="feedback_draft",placeholder="Which page, season and team? What did you expect to see?")
        st.caption("This form does not send anything. Download your note and share it with the project owner; no GitHub account is needed to create the note.")
        st.download_button("Download feedback note",f"CourtSense {APP_VERSION}\nRun: {results.get('run_id')}\n\n{feedback}",file_name="courtsense_feedback.txt",mime="text/plain")
