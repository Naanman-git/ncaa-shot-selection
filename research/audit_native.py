from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ncaa_shot_selection import load_native_shots, prepare_shots


def main() -> None:
    raw = load_native_shots(ROOT / "data/raw", seasons=(2023, 2024, 2025))
    clean, cleaning = prepare_shots(raw)
    season_rows = []
    for season, d in clean.groupby("season", sort=True):
        season_rows.append({
            "season": int(season),
            "rows": len(d),
            "games": int(d.contest_id.nunique()),
            "teams": int(d.team_id.nunique()),
            "shooters": int(d.shooter_id.nunique()),
            "make_rate": float(d.made.mean()),
            "three_point_share": float((d.point_value == 3).mean()),
            "coordinate_rows": int(d[["shot_x", "shot_y"]].notna().all(axis=1).sum()),
            "zones": d.shot_zone.value_counts().to_dict(),
            "team_rows": d.groupby("team_id").size().describe().to_dict(),
        })
    manifest = []
    for p in sorted((ROOT / "data/raw").glob("ncaa_mbb_shots_*.parquet")):
        manifest.append({
            "file": str(p.relative_to(ROOT)),
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "url": f"https://github.com/sportsdataverse/sportsdataverse-data/releases/download/ncaa_mbb_shots/{p.name}",
        })
    result = {
        "source": "SportsDataverse ncaa_mbb_shots",
        "source_documentation": "https://github.com/sportsdataverse/hoopR/blob/main/R/load_ncaa_mbb.R",
        "seasons": season_rows,
        "cleaning": cleaning,
        "missingness_after_cleaning": clean.isna().sum().to_dict(),
        "source_files": manifest,
        "limitations": [
            "The source shot table has no complete season-type field; regular-season filtering needs a documented crosswalk.",
            "The source has no defender distance, shot-clock time, or shot-mechanism feature.",
            "Exact duplicate rows are removed; near-identical shots are retained because they can represent real attempts.",
        ],
    }
    (ROOT / "research/native_audit_results.json").write_text(json.dumps(result, indent=2, default=str))
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
