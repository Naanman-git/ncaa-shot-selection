from __future__ import annotations
from pathlib import Path
from typing import Iterable
import pandas as pd

REQUIRED=["season","team_id","shooter_id","shot_x","shot_y","dist_ft","shot_zone","made","point_value","contest_id"]

def load_native_shots(raw_dir: str|Path, seasons: Iterable[int]=(2023,2024,2025,2026)) -> pd.DataFrame:
    frames=[]; raw=Path(raw_dir)
    for season in seasons:
        p=raw/f"ncaa_mbb_shots_{season}.parquet"
        if p.exists():
            x=pd.read_parquet(p); x["source_file"]=p.name; frames.append(x)
    if not frames: raise FileNotFoundError("No native NCAA shot files found")
    return pd.concat(frames,ignore_index=True)

def _reconciled(raw, root):
    x=raw.copy(); x["espn_game_id"]=x.espn_game_id.astype(str); x["espn_team_id"]=x.espn_team_id.astype(str)
    x["_three"]=(x.point_value==3).astype(int); x["_made"]=x.made.astype(int)
    agg=x.groupby(["season","espn_game_id","espn_team_id"],dropna=False).agg(
        fga=("made","size"),fgm=("_made","sum"),threepa=("_three","sum"),
        threem=("_three",lambda s: int(((s==1)&(x.loc[s.index,"made"]==1)).sum()))).reset_index()
    boxes=[]
    for season in sorted(x.season.unique()):
        p=Path(root)/"data/raw"/f"team_box_{int(season)}.parquet"
        if p.exists(): boxes.append(pd.read_parquet(p))
    b=pd.concat(boxes,ignore_index=True); b["game_id"]=b.game_id.astype(str); b["team_id"]=b.team_id.astype(str)
    b=b.rename(columns={"game_id":"espn_game_id","team_id":"espn_team_id","field_goals_attempted":"box_fga","field_goals_made":"box_fgm","three_point_field_goals_attempted":"box_threepa","three_point_field_goals_made":"box_threem"})
    cols=["season","espn_game_id","espn_team_id","box_fga","box_fgm","box_threepa","box_threem","game_date","season_type","team_display_name"]
    b=b[cols].drop_duplicates(["season","espn_game_id","espn_team_id"])
    m=agg.merge(b,on=["season","espn_game_id","espn_team_id"],how="inner")
    m["match"]=(m.fga==m.box_fga)&(m.fgm==m.box_fgm)&(m.threepa==m.box_threepa)&(m.threem==m.box_threem)
    good=m[m.match].groupby(["season","espn_game_id"]).espn_team_id.nunique()
    good=good[good>=2].reset_index()[["season","espn_game_id"]]
    out=x.merge(good,on=["season","espn_game_id"],how="inner")
    out=out.merge(m[["season","espn_game_id","espn_team_id","game_date","season_type","team_display_name"]],on=["season","espn_game_id","espn_team_id"],how="left")
    out["team_name"]=out["team_display_name"].fillna(out["team_id"])
    return out,{"candidate_games":int(x.espn_game_id.nunique()),"reconciled_games":int(good.espn_game_id.nunique()),"rows_in_reconciled_games":len(out),"matched_team_games":int(m.match.sum()),"team_games":len(m)}

def prepare_shots(raw: pd.DataFrame, root: str|Path|None=None):
    missing=[c for c in REQUIRED if c not in raw]
    if missing: raise ValueError(f"Missing required columns: {missing}")
    x=raw.copy(); report={"rows_before":len(x),"exact_duplicate_rows_retained":int(x.duplicated().sum())}
    if root is not None: x,rec=_reconciled(x,root); report.update(rec)
    valid=x[REQUIRED].notna().all(axis=1)&x.point_value.isin([2,3]); x=x.loc[valid].copy()
    x["made"]=x.made.astype(bool); x["player_name"]=x.get("shooter_clean_name",x.shooter_id).fillna(x.shooter_id)
    x["player_key"]=x.get("shooter_player_id",x.shooter_id).fillna(x.shooter_id).astype(str)
    x["shot_uid"]=(x.season.astype(str)+":"+x.espn_game_id.astype(str)+":"+x.espn_team_id.astype(str)+":"+x.index.astype(str))
    report.update({"rows_in_model":len(x),"rows_excluded_from_model":int((~valid).sum()),"seasons":sorted(x.season.unique().tolist()),"geometry_inferred_point_value":True,"source_duplicate_policy":"retain; no event key is available","zones":x.shot_zone.value_counts().to_dict()})
    return x.reset_index(drop=True),report
