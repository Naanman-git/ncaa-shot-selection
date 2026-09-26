"""Build a single versioned evidence source for app, paper and deck."""
from __future__ import annotations
import hashlib
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.exceptions import ConvergenceWarning

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from ncaa_shot_selection.modeling import add_history, make_model, calibration, game_bootstrap_metrics, ZONES
from ncaa_shot_selection.product import run_scenario


def checksum(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    config = json.loads((ROOT/"config/analysis.json").read_text())
    path = ROOT/"data/processed/shots_clean.parquet"
    print("Preparing strictly prior-day history", flush=True)
    d = pd.read_parquet(path)
    if "team_name" not in d:
        d["team_name"] = d.team_id
    if "player_name" not in d:
        d["player_name"] = d.shooter_clean_name.fillna(d.shooter_id)
    if "player_key" not in d:
        raise ValueError("Validated identity contract is required")
    if set(config["training_seasons"]+[config["selection_season"], config["final_test_season"]])-set(d.season):
        raise ValueError("All four seasons are required by the frozen protocol")
    d = add_history(d)
    train = d[d.season.isin(config["training_seasons"])]
    global_p = float(train.made.mean())
    zone = train.groupby("shot_zone", observed=True).made.agg(["sum", "count"])
    zone_prior = ((zone["sum"]+30*global_p)/(zone["count"]+30)).to_dict()
    preds = {"Global rate": np.full(len(d), global_p),
             "Zone shrinkage": d.shot_zone.astype(str).map(zone_prior).to_numpy(float)}
    fitted = {}
    for name, history in [("Spatial logistic", False),("Spatial + player history", True)]:
        print("Fitting "+name, flush=True)
        model = make_model(history)
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            model.fit(train, train.made.astype(int))
        preds[name] = model.predict_proba(d)[:,1]
        fitted[name] = model
    rows = []
    # Select using 2025 only, before computing final-season metrics.
    for name in config["candidates"]:
        mask = d.season.eq(config["selection_season"]).to_numpy()
        y, p = d.loc[mask,"made"].astype(int), preds[name][mask]
        rows.append({"model":name,"season":config["selection_season"],"n":len(y),
                     "brier":float(brier_score_loss(y,p)),"log_loss":float(log_loss(y,p,labels=[0,1]))})
    chosen = min(rows,key=lambda r:r["log_loss"])["model"]
    print("Selected on 2025: "+chosen+"; evaluating fixed 2026 test", flush=True)
    out = ROOT/"data/outputs"
    out.mkdir(exist_ok=True,parents=True)
    (out/"model_selection.json").write_text(json.dumps({"config_sha256":checksum(ROOT/"config/analysis.json"),
        "selected_model":chosen,"selection_metrics":rows},indent=2))
    mask = d.season.eq(config["final_test_season"]).to_numpy()
    for name in config["candidates"]:
        y,p = d.loc[mask,"made"].astype(int),preds[name][mask]
        rows.append({"model":name,"season":config["final_test_season"],"n":len(y),
                     "brier":float(brier_score_loss(y,p)),"log_loss":float(log_loss(y,p,labels=[0,1]))})
    d["model_p"] = preds[chosen]
    ci = game_bootstrap_metrics(d[mask],preds[chosen][mask],preds["Zone shrinkage"][mask],
                               config["seed"],config["bootstrap_repeats"])
    calibration_rows=[]
    for season in [config["selection_season"],config["final_test_season"]]:
        part=d[d.season==season]
        calibration_rows += [{"season":season,**r} for r in calibration(part.made,part.model_p)]
    team=config["case_study_team"]
    case=d[(d.season==config["final_test_season"])&d.team_name.eq(team)]
    if len(case)<80:
        raise ValueError("Prespecified case study lacks enough support; do not substitute a favorable team")
    scenario=run_scenario(case,**config["scenario"],prior_rates=zone_prior)
    scenario["table"]=scenario["table"].to_dict("records")
    scenario.update(team=team,season=config["final_test_season"],attempts=len(case),
                    games=int(case.contest_id.nunique()),settings=config["scenario"])
    sensitivity=[]
    for shift in [.025,.05,.10]:
        for risk in [0.,1.,2.]:
            result=run_scenario(case,max_shift=shift,risk=risk,prior_rates=zone_prior)
            sensitivity.append({"max_shift":shift,"risk":risk,
                **{k:result[k] for k in ["gain_per100","gain_low","gain_high","feasible"]}})

    # Prespecified, interpretable checks that correspond to the blueprint's
    # four substantive hypotheses. These use only the frozen final-test
    # predictions and the separately defined scenario estimates.
    test = d.loc[mask].copy()
    test["predicted_ep"] = test.model_p * test.point_value
    distance_edges = [0, 5, 10, 15, 20, 23, 26, 30, 40, 100]
    test["distance_band"] = pd.cut(test.dist_ft, distance_edges, right=False)
    distance_profile = (test.groupby("distance_band", observed=True)
        .agg(attempts=("made", "size"), observed_fg=("made", "mean"),
             predicted_fg=("model_p", "mean"), mean_distance=("dist_ft", "mean"))
        .reset_index())
    distance_rho = float(distance_profile.mean_distance.corr(
        distance_profile.predicted_fg, method="spearman"))
    distance_rows = [{"distance_band": str(row.distance_band),
                      "attempts": int(row.attempts),
                      "observed_fg": float(row.observed_fg),
                      "predicted_fg": float(row.predicted_fg)}
                     for row in distance_profile.itertuples()]

    zone_test = (test.groupby("shot_zone", observed=True)
        .agg(attempts=("made", "size"), observed_fg=("made", "mean"),
             predicted_fg=("model_p", "mean"), predicted_ep=("predicted_ep", "mean")))
    corner = zone_test.loc["corner3"]
    paint = zone_test.loc["paint"]
    h2_supported = bool(corner.predicted_fg < paint.predicted_fg and
                        corner.predicted_ep > paint.predicted_ep)
    max_shrink = max(scenario["table"],
                     key=lambda row: abs(row["shrunk_fg"] - row["raw_fg"]))
    selected_test = next(row for row in rows
                         if row["season"] == config["final_test_season"] and row["model"] == chosen)
    zone_test_score = next(row for row in rows
                           if row["season"] == config["final_test_season"] and
                           row["model"] == "Zone shrinkage")
    hypothesis_results = [
        {"id": "H1", "hypothesis": "Predicted make probability decreases as distance increases.",
         "method": "Spearman association across prespecified held-out distance bands.",
         "result": f"Spearman rho = {distance_rho:.3f} across {len(distance_rows)} bands.",
         "status": "supported" if distance_rho < -0.8 else "mixed"},
        {"id": "H2", "hypothesis": "A lower-probability three-point zone can have higher expected value than a two-point zone.",
         "method": "Compare held-out corner-three and paint averages from the frozen model.",
         "result": (f"Corner three: {corner.predicted_fg:.1%} predicted FG and "
                    f"{corner.predicted_ep:.3f} EP; paint: {paint.predicted_fg:.1%} predicted FG and "
                    f"{paint.predicted_ep:.3f} EP."),
         "status": "supported" if h2_supported else "not supported"},
        {"id": "H3", "hypothesis": "Raw zone rates move toward pooled estimates after shrinkage.",
         "method": "Compare raw and 30-attempt-prior rates in the prespecified case study.",
         "result": (f"Largest change: {max_shrink['zone']}, {max_shrink['raw_fg']:.1%} raw to "
                    f"{max_shrink['shrunk_fg']:.1%} shrunk."),
         "status": "supported"},
        {"id": "H4", "hypothesis": "Spatial and prior player history improve held-out probability prediction over a zone baseline.",
         "method": "Compare final-test Brier score and log loss after model selection was frozen.",
         "result": (f"Selected model improved Brier by {zone_test_score['brier']-selected_test['brier']:.4f} "
                    f"and log loss by {zone_test_score['log_loss']-selected_test['log_loss']:.4f}."),
         "status": "supported" if selected_test["log_loss"] < zone_test_score["log_loss"] else "not supported"},
    ]

    selected_pipeline = fitted[chosen]
    feature_names = selected_pipeline.named_steps["features"].get_feature_names_out()
    coefficients = selected_pipeline.named_steps["model"].coef_[0]
    interpretable = {
        name: float(value) for name, value in zip(feature_names, coefficients)
        if name in {"angle__abs_angle", "history__history_logit", "history__history_size"}
    }
    model_interpretation = [
        {"feature": "Shot angle (1 SD)", "coefficient": interpretable["angle__abs_angle"],
         "odds_multiplier": float(np.exp(interpretable["angle__abs_angle"])),
         "interpretation": "Association for a one-standard-deviation increase in absolute angle, holding transformed model inputs fixed."},
        {"feature": "Prior player-zone make tendency (1 SD)",
         "coefficient": interpretable["history__history_logit"],
         "odds_multiplier": float(np.exp(interpretable["history__history_logit"])),
         "interpretation": "Association for stronger strictly prior-day player-zone history."},
        {"feature": "Prior player-zone sample size (1 SD)",
         "coefficient": interpretable["history__history_size"],
         "odds_multiplier": float(np.exp(interpretable["history__history_size"])),
         "interpretation": "Association for a larger log prior-attempt count after controlling for the prior make tendency."},
    ]
    audit_path=ROOT/"research/native_audit_results.json"
    audit=json.loads(audit_path.read_text()) if audit_path.exists() else {}
    season_summary=[]
    for season,part in d.groupby("season"):
        season_summary.append({"season":int(season),"attempts":len(part),
            "games":int(part.contest_id.nunique()),"teams":int(part.team_name.nunique()),
            "players":int(part.player_key.nunique()),"fg_pct":float(part.made.mean()),
            "date_start":str(part.game_day.min().date()),"date_end":str(part.game_day.max().date())})
    limitations=[
        "Filtered, reconciled NCAA Division I men versus men cohort; not complete NCAA coverage.",
        "Native chart coordinates are discretized. Geometry and aggregate box checks do not establish shot-level tracking accuracy.",
        "No defender distance, play context, shot clock or reliable period timing; predictions describe recorded locations and prior shooting history.",
        "Online chronological evaluation: earlier test-date outcomes may update player histories; current and future outcomes are excluded.",
        "Model probabilities are evaluated with calibration curves; no separate post-hoc calibration transform is applied.",
        "Scenario uses 30-attempt shrinkage of selected-scope zone rates, separate from the predictive model; player suggestions with sparse zones are frozen.",
        "Bootstrap ranges resample games and condition on a fixed chosen mix. They exclude policy selection and causal uncertainty.",
        "A higher estimated scenario score is not evidence of improved game outcomes. Defensive response, possession changes and free throws are omitted.",
        "Anonymous or abbreviated identities and partial reconciliation can introduce coverage bias; consult the data audit.",
        "Public access and code licensing do not establish permission to redistribute the upstream sports data."
    ]
    digest=checksum(path)
    results={"run_id":"ncaa-"+digest[:10]+"-"+checksum(ROOT/"config/analysis.json")[:8],
        "generated_utc":datetime.now(timezone.utc).isoformat(),"config":config,
        "data_sha256":digest,"config_sha256":checksum(ROOT/"config/analysis.json"),
        "selected_model":chosen,"model_comparison":rows,"calibration":calibration_rows,
        "test_confidence_intervals":ci,"season_summary":season_summary,"audit":audit,
        "zone_prior":zone_prior,"scenario":scenario,"sensitivity":sensitivity,
        "hypothesis_results":hypothesis_results,"distance_profile":distance_rows,
        "model_interpretation":model_interpretation,"limitations":limitations,
        "model_spec":{"training":"2022–23 and 2023–24", "selection":"2024–25", "final_test":"2025–26",
            "features":["five chart zones","cubic distance spline (5 knots)","absolute angle",
                        "prior-day player-zone make rate (30 fixed-prior attempts)","log prior attempts"],
            "estimator":"L2 logistic regression; C=1; maximum 300 iterations; train-only transformations",
            "bootstrap":"500 paired game-cluster resamples; seed 42; 2.5th–97.5th percentiles",
            "prediction_target":"Probability that an attempted field goal is made",
            "scenario_target":"Conditional points per recorded field-goal attempt; excludes free throws and possession value"}}
    (out/"final_results.json").write_text(json.dumps(results,indent=2,allow_nan=False))
    joblib.dump({"selected_model":chosen,"models":fitted,"zone_prior":zone_prior,
                 "global_p":global_p,"config":config},out/"probability_model.joblib")
    d.to_parquet(ROOT/"data/processed/shots_scored.parquet",index=False,compression="zstd")
    pd.DataFrame(rows).to_csv(out/"model_comparison.csv",index=False)
    pd.DataFrame(scenario["table"]).to_csv(out/"case_study_scenario.csv",index=False)
    print(json.dumps({"run_id":results["run_id"],"selected_model":chosen,"season_summary":season_summary,
                      "test_intervals":ci,"scenario_gain":scenario["gain_per100"]},indent=2),flush=True)


if __name__=="__main__":
    main()
