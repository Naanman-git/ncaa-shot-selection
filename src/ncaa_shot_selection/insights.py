"""Descriptive insights and report cards; these do not change the frozen model."""
from html import escape
import numpy as np
import pandas as pd
from .charts import ZONE_NAMES
from .product import scope_summary

APP_VERSION = "1.1.0"


def zone_evidence(frame):
    table = scope_summary(frame)["zone_table"]
    if table.empty:
        return table
    games = frame.groupby("shot_zone", observed=True).contest_id.nunique()
    table["games"] = table.shot_zone.map(games).astype(int)
    # These are transparent sample-support labels, not calibrated probabilities.
    table["support"] = np.select(
        [(table["count"] >= 100) & (table.games >= 10),
         (table["count"] >= 30) & (table.games >= 5)],
        ["Broader sample", "Usable sample"], default="Limited sample")
    table["gap"] = table.observed_pps - table.expected_pps
    return table


def game_trend(frame):
    work = frame.assign(points=frame.made * frame.point_value,
                        expected=frame.model_p * frame.point_value)
    out = work.groupby(["game_date", "contest_id"], observed=True).agg(
        attempts=("made", "size"), makes=("made", "sum"),
        points=("points", "sum"), expected=("expected", "sum")).reset_index()
    out = out.sort_values(["game_date", "contest_id"])
    out["Observed points / attempt"] = out.points / out.attempts
    out["Predicted points / attempt"] = out.expected / out.attempts
    # Ratio of sums prevents a two-shot game receiving the same weight as twenty shots.
    out["Recent 5 games · observed"] = out.points.rolling(5, min_periods=1).sum() / out.attempts.rolling(5, min_periods=1).sum()
    return out


def points_interval(frame, repeats=500, seed=42):
    """Game-cluster interval for observed points per attempt, ratio of totals."""
    g = frame.assign(points=frame.made * frame.point_value).groupby("contest_id").agg(
        n=("made", "size"), points=("points", "sum"))
    if len(g) < 5:
        return None
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(g), size=(repeats, len(g)))
    estimates = g.points.to_numpy()[indices].sum(axis=1) / g.n.to_numpy()[indices].sum(axis=1)
    return tuple(float(x) for x in np.quantile(estimates, [.025, .975]))


def report_card(team, season, frame, scenario, results):
    """Self-contained, printable HTML; untrusted source labels are escaped."""
    s = scope_summary(frame)
    zones = zone_evidence(frame)
    good = zones[zones.support != "Limited sample"]
    strongest = "Insufficient zone evidence"
    review = "Collect more observations before choosing a priority."
    if not good.empty:
        best = good.loc[good.observed_pps.idxmax()]
        weakest = good.loc[good.gap.idxmin()]
        strongest = f"{ZONE_NAMES.get(best.shot_zone, best.shot_zone)} ({best.observed_pps:.2f} observed points/attempt)"
        review = f"Review {ZONE_NAMES.get(weakest.shot_zone, weakest.shot_zone).lower()} attempts on video: the observed-minus-predicted gap is {weakest.gap:+.2f} points/attempt. This is a review prompt, not proof of a skill deficit."
    opportunity = "No feasible scenario for this sample."
    if scenario.get("feasible"):
        opportunity = (f"Default constrained scenario: {scenario['gain_per100']:+.1f} estimated points per 100 attempts; "
                       f"conditional 95% interval {scenario['gain_low']:+.1f} to {scenario['gain_high']:+.1f}.")
    rows = "".join(f"<tr><td>{escape(ZONE_NAMES.get(r.shot_zone, r.shot_zone))}</td><td>{r.count:,}</td>"
                   f"<td>{r.fg_pct:.1%}</td><td>{r.observed_pps:.2f}</td><td>{r.expected_pps:.2f}</td>"
                   f"<td>{escape(r.support)}</td></tr>" for r in zones.itertuples())
    interval = points_interval(frame)
    ci = "Fewer than five games: interval withheld." if interval is None else f"Game-resampling 95% interval for observed points/attempt: {interval[0]:.2f}–{interval[1]:.2f}."
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CourtSense · {escape(team)} report card</title><style>
body{{font:15px/1.45 system-ui,sans-serif;color:#172b3a;background:#fcfaf5;max-width:900px;margin:32px auto;padding:24px}}
h1{{font-size:30px;margin:8px 0}}h2{{font-size:17px;margin:18px 0 6px}}.kicker{{color:#167d8d;letter-spacing:.08em}}
.stats{{display:flex;gap:14px;flex-wrap:wrap;margin:20px 0}}.stats div{{background:#edf3ef;padding:12px;flex:1;min-width:130px}}strong{{display:block;font-size:23px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}td,th{{text-align:left;border-bottom:1px solid #d8dedb;padding:7px}}.small{{font-size:12px;color:#52636c}}
@page{{size:A4;margin:14mm}}@media print{{body{{margin:0;padding:0;font-size:11px;background:white}}h1{{font-size:24px}}h2{{font-size:14px}}table{{font-size:10px}}.stats{{margin:12px 0}}.small{{font-size:10px}}}}
</style><p class="kicker">COURTSENSE · NCAA DIVISION I MEN</p><h1>{escape(team)}</h1><p>{season-1}–{str(season)[-2:]} · Team report card</p>
<div class="stats"><div>Recorded attempts<strong>{s['count']:,}</strong></div><div>Games represented<strong>{s['games']}</strong></div><div>Field-goal %<strong>{s['fg_pct']:.1%}</strong></div><div>Points / attempt<strong>{s['observed_pps']:.2f}</strong></div></div>
<p class="small">{escape(ci)}</p><h2>Strongest observed zone with usable support</h2><p>{escape(strongest)}</p><h2>Video-review priority</h2><p>{escape(review)}</p>
<h2>Estimated opportunity</h2><p>{escape(opportunity)}</p><p class="small">Default limits: ±5 percentage points per zone, 20-point total movement budget, 60% three-point cap, uncertainty penalty 1.0.</p>
<table><thead><tr><th>Zone</th><th>Attempts</th><th>FG%</th><th>Observed pts/att</th><th>Predicted pts/att</th><th>Support</th></tr></thead><tbody>{rows}</tbody></table>
<p class="small">Support: usable = at least 30 attempts across 5 games; broader = at least 100 across 10 games. These labels describe sample size, not a probability that advice is correct.</p>
<h2>Interpret with care</h2><p class="small">Partial source coverage, not a complete season guarantee. Scenarios assume unchanged zone efficiency and are not intervention results. Free throws, turnovers and rebounds are outside the shot model. Opponents, defenders and shot availability can affect these results. Training-season predictions are in-sample; later evaluation seasons provide stronger evidence.</p>
<p class="small">SportsDataverse NCAA shot data · Analysis built {escape(str(results.get('generated_utc','unknown'))[:10])} · Run {escape(str(results.get('run_id','unknown')))} · App {APP_VERSION}. Open in a browser and choose Print → Save as PDF.</p></html>"""


def possession_estimates(boxes):
    """Pair two team boxes and average their estimated possessions; reject bad rows."""
    b = boxes.copy()
    keys = ["season", "game_id", "team_id"]
    if b.duplicated(keys).any():
        raise ValueError("Duplicate team-game box scores")
    numeric = ["field_goals_attempted", "free_throws_attempted", "offensive_rebounds", "total_turnovers", "team_score"]
    for c in numeric:
        b[c] = pd.to_numeric(b[c], errors="coerce")
    valid = b[numeric].notna().all(axis=1) & (b[numeric] >= 0).all(axis=1)
    b["raw_possessions"] = b.field_goals_attempted - b.offensive_rebounds + b.total_turnovers + .475 * b.free_throws_attempted
    b = b.loc[valid & (b.raw_possessions > 0)].copy()
    groups = b.groupby(["season", "game_id"])
    b = b.loc[groups.team_id.transform("nunique") == 2].copy()
    b["estimated_possessions"] = b.groupby(["season", "game_id"]).raw_possessions.transform("mean")
    return b
