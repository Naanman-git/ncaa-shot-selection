import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/analyze_prospective_validation.py"
SPEC = importlib.util.spec_from_file_location("prospective", SCRIPT)
prospective = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prospective)


def sample_data():
    rows = []
    number = 0
    for session in ["S1", "S2", "S3", "S4"]:
        for strategy, block_order in [("current", 1), ("recommended", 2)]:
            for attempt in range(1, 11):
                number += 1
                made = int((attempt + block_order) % (3 if strategy == "current" else 2) == 0)
                rows.append({
                    "shot_id": f"A{number}", "participant_code": "P1",
                    "session_id": session, "block_id": f"{session}-{strategy}",
                    "block_order": block_order, "strategy": strategy,
                    "attempt_order": attempt, "shot_x": 0.0, "shot_y": 5.0,
                    "zone": "rim", "made": made, "point_value": 2,
                    "model_probability": 0.55, "notes": "",
                })
    return pd.DataFrame(rows)


def test_analyze_reports_probability_and_strategy_metrics():
    result = prospective.analyze(sample_data(), repeats=100, seed=7)
    assert result["attempts"] == 80
    assert result["sessions"] == 4
    assert 0 <= result["probability_validation"]["brier"] <= 1
    assert result["strategy_interval"]["cluster"] == "session_id"
    assert len(result["strategy_results"]) == 2


def test_duplicate_attempts_are_rejected():
    data = sample_data()
    data.loc[1, "shot_id"] = data.loc[0, "shot_id"]
    with pytest.raises(ValueError, match="unique"):
        prospective.analyze(data, repeats=20)


def test_both_strategy_arms_are_required():
    data = sample_data().query("strategy == 'current'")
    with pytest.raises(ValueError, match="both current and recommended"):
        prospective.analyze(data, repeats=20)
