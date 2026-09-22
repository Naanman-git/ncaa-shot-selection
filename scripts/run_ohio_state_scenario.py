from __future__ import annotations

import json
from pathlib import Path
import sys

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ncaa_shot_selection.optimization import optimize_mix


def main() -> None:
    data = pd.read_parquet(ROOT / "data/processed/shots_clean.parquet")
    model = joblib.load(ROOT / "data/outputs/probability_model.joblib")
    team_name = "Ohio St."
    attempts = data[(data.season == 2025) & (data.team_id == team_name)].copy()
    if attempts.empty:
        raise ValueError(f"{team_name} is not present in the selected evaluation season")
    p = model.predict_proba(attempts[["shot_zone", "point_value", "dist_ft"]])[:, 1]
    scenario = optimize_mix(attempts, p)
    output = {
        "team": team_name,
        "season": 2025,
        "attempts": len(attempts),
        "zones": scenario.zones,
        "current_share": scenario.current_share.tolist(),
        "recommended_share": scenario.recommended_share.tolist(),
        "expected_points_by_zone": scenario.expected_points_by_zone.tolist(),
        "current_expected_points_per_attempt": scenario.current_expected_points,
        "recommended_expected_points_per_attempt": scenario.recommended_expected_points,
        "estimated_change_per_100_attempts": 100 * (scenario.recommended_expected_points - scenario.current_expected_points),
        "solver_status": scenario.status,
        "interpretation": "Conditional model scenario using 2025 observed Ohio State attempt features and a 2023-trained probability model; not a causal strategy result.",
    }
    out = ROOT / "data/outputs"
    (out / "ohio_state_scenario.json").write_text(json.dumps(output, indent=2))
    print(json.dumps(output, indent=2))


if __name__ == "__main__": main()
