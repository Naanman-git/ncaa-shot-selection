from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ncaa_shot_selection import load_native_shots, prepare_shots


def test_clean_table_has_required_model_contract():
    raw = load_native_shots(ROOT / "data/raw", seasons=(2023,))
    clean, report = prepare_shots(raw)
    assert len(clean) > 600_000
    assert report["rows_in_model"] == len(clean)
    assert clean[["contest_id", "team_id", "shooter_id", "shot_zone", "shot_x", "shot_y", "dist_ft", "point_value", "made"]].notna().all().all()
    assert set(clean["point_value"].unique()) == {2, 3}
    assert clean["shot_zone"].isin({"rim", "paint", "mid", "corner3", "abovebreak3"}).all()


def test_exact_duplicates_are_retained_without_event_key():
    raw = load_native_shots(ROOT / "data/raw", seasons=(2023,))
    clean, report = prepare_shots(raw)
    assert report["exact_duplicate_rows_retained"] > 0
    assert report["source_duplicate_policy"].startswith("retain")
