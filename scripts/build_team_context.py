"""Join existing validated shot games to source box scores; write aggregate context."""
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone
import pandas as pd
from ncaa_shot_selection.insights import possession_estimates

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,default=ROOT/'data/app')
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    fields = ["season", "espn_game_id", "espn_team_id", "team_name", "contest_id", "made", "point_value"]
    shots = pd.read_parquet(ROOT / "data/processed/shots_scored.parquet", columns=fields)
    shots["made_three"] = shots.made.astype(int) * (shots.point_value == 3)
    shots["three"] = (shots.point_value == 3).astype(int)
    counts = shots.groupby(["season", "espn_game_id", "espn_team_id", "team_name"], observed=True).agg(
        shot_attempts=("made", "size"), shot_makes=("made", "sum"), three_attempts=("three", "sum"),
        three_makes=("made_three", "sum")).reset_index().rename(columns={"espn_game_id": "game_id", "espn_team_id": "team_id"})
    files = [ROOT / f"data/raw/team_box_{year}.parquet" for year in sorted(shots.season.unique())]
    b = pd.concat([pd.read_parquet(p) for p in files], ignore_index=True)
    for frame in (b, counts):
        for c in ("game_id", "team_id"):
            frame[c] = frame[c].astype(str)
    b = b.drop(columns="team_name", errors="ignore")
    joined = counts.merge(b, on=["season", "game_id", "team_id"], validate="one_to_one")
    ok = ((joined.shot_attempts == joined.field_goals_attempted)
          & (joined.shot_makes == joined.field_goals_made)
          & (joined.three_attempts == joined.three_point_field_goals_attempted)
          & (joined.three_makes == joined.three_point_field_goals_made)
          & (2*joined.field_goals_made + joined.three_point_field_goals_made + joined.free_throws_made == joined.team_score))
    paired = possession_estimates(joined.loc[ok])
    paired["designation"] = paired.team_home_away.fillna("unknown")
    # Source home/away is a box designation, not verified arena or neutral-site status.
    out = paired.groupby(["season", "team_name", "designation"], observed=True).agg(
        games=("game_id", "nunique"), points=("team_score", "sum"), possessions=("estimated_possessions", "sum"),
        attempts=("field_goals_attempted", "sum"), makes=("field_goals_made", "sum"),
        threes=("three_point_field_goals_made", "sum"), free_throws=("free_throws_made", "sum"),
        free_throw_attempts=("free_throws_attempted", "sum"), turnovers=("total_turnovers", "sum"),
        offensive_rebounds=("offensive_rebounds", "sum")).reset_index()
    out.to_parquet(args.output_dir / "team_context.parquet", index=False, compression="zstd")
    meta = {"built_utc": datetime.now(timezone.utc).isoformat(), "candidate_team_games": len(counts),
            "matched_boxes": len(joined), "reconciled_team_games": len(paired),
            "excluded_team_games": len(counts)-len(paired), "aggregate_rows": len(out),
            "formula": "FGA - offensive rebounds + total turnovers + 0.475 * FTA; average both teams per game",
            "sources": [{"file": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
            "attribution": "SportsDataverse / hoopR.mbb authors; ESPN-origin team box scores; transformed and aggregated by CourtSense",
            "license_url": "https://github.com/sportsdataverse/hoopR-mbb-data/blob/main/LICENSE.md",
            "method_url": "https://kenpom.com/blog/ratings-glossary/",
            "limits": "Estimated possessions, no possession sequence reconstruction; unadjusted for schedule. Home/away designations may include neutral-site games."}
    (args.output_dir / "context_manifest.json").write_text(json.dumps(meta, indent=2)+"\n")
    print(json.dumps({k:v for k,v in meta.items() if k not in {"sources"}}, indent=2))


if __name__ == "__main__":
    main()
