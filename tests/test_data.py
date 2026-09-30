from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ncaa_shot_selection import load_native_shots, prepare_shots


@pytest.mark.skipif(not (ROOT / 'data/raw/ncaa_mbb_shots_2023.parquet').exists(), reason='Full raw-source integration requires local downloads')
def test_clean_table_has_required_model_contract():
    raw = load_native_shots(ROOT / "data/raw", seasons=(2023,))
    clean, report = prepare_shots(raw)
    assert len(clean) > 600_000
    assert report["rows_in_model"] == len(clean)
    assert clean[["contest_id", "team_id", "shooter_id", "shot_zone", "shot_x", "shot_y", "dist_ft", "point_value", "made"]].notna().all().all()
    assert set(clean["point_value"].unique()) == {2, 3}
    assert clean["shot_zone"].isin({"rim", "paint", "mid", "corner3", "abovebreak3"}).all()


def fixture_shots():
    return pd.DataFrame([
        dict(season=2023, team_id='A', shooter_id='P', espn_game_id='G',
             espn_team_id='A', contest_id='G', shot_x=25., shot_y=5., dist_ft=2.,
             shot_zone='rim', made=True, point_value=2),
        dict(season=2023, team_id='B', shooter_id='Q', espn_game_id='G',
             espn_team_id='B', contest_id='G', shot_x=2., shot_y=5., dist_ft=23.,
             shot_zone='corner3', made=False, point_value=3),
    ])


def test_exact_duplicates_are_retained_without_event_key():
    raw = pd.concat([fixture_shots(), fixture_shots()], ignore_index=True)
    clean, report = prepare_shots(raw)
    assert report["exact_duplicate_rows_retained"] == 2
    assert len(clean) == 4
    assert clean.shot_uid.is_unique
    assert report["source_duplicate_policy"].startswith("retain")


def test_loader_and_cleaning_contract_without_local_downloads(tmp_path):
    raw = fixture_shots()
    invalid = raw.iloc[[0]].copy()
    invalid['shot_x'] = None
    pd.concat([raw, invalid], ignore_index=True).to_parquet(tmp_path / 'ncaa_mbb_shots_2023.parquet')
    loaded = load_native_shots(tmp_path, seasons=(2023, 2024))
    clean, report = prepare_shots(loaded)
    assert len(clean) == 2
    assert report['rows_excluded_from_model'] == 1
    assert clean.point_value.tolist() == [2, 3]
    assert clean.player_key.tolist() == ['P', 'Q']
    assert clean.source_file.unique().tolist() == ['ncaa_mbb_shots_2023.parquet']
