"""Read-only feasibility audit. No model training or test-set optimization.

Run with a Python environment containing pandas and pyarrow. Writes JSON evidence.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research'
FG_TYPES = ['JumpShot', 'LayUpShot', 'DunkShot', 'TipShot']

def native(x):
    if isinstance(x, (np.integer, np.floating)): return x.item()
    if isinstance(x, np.bool_): return bool(x)
    if isinstance(x, (pd.Timestamp, datetime)): return x.isoformat()
    raise TypeError(type(x).__name__)

def analyze_season(year):
    s = pd.read_parquet(ROOT / f'data/raw/shots_{year}.parquet')
    b = pd.read_parquet(ROOT / f'data/raw/team_box_{year}.parquet')
    # Non-free-throw event classes with documented attempted point values.
    fg_type = s.type_text.isin(FG_TYPES)
    fg = s[fg_type & s.score_value.isin([2, 3])].copy()
    fg['made'] = fg.scoring_play.astype(int)
    fg['three'] = (fg.score_value == 3).astype(int)
    fg['three_made'] = fg.three * fg.made
    fg['has_xy'] = fg.coordinate_x_raw.notna() & fg.coordinate_y_raw.notna()
    # Broad source-coordinate bounds only; this does NOT certify geometry.
    fg['bounded_xy'] = fg.has_xy & fg.coordinate_x_raw.between(0,50) & fg.coordinate_y_raw.between(-6,94)
    fg['sentinel_xy'] = fg.has_xy & ((fg.coordinate_x_raw.abs()>1000) | (fg.coordinate_y_raw.abs()>1000))
    g = fg.groupby(['game_id','team_id']).agg(fga=('made','size'),fgm=('made','sum'),tpa=('three','sum'),tpm=('three_made','sum'),xy=('bounded_xy','sum')).reset_index()
    g = g.merge(b[['game_id','team_id','field_goals_attempted','field_goals_made','three_point_field_goals_attempted','three_point_field_goals_made','season_type','game_date']],on=['game_id','team_id'],how='left',validate='one_to_one',indicator=True)
    g['box_match'] = ((g.fga==g.field_goals_attempted)&(g.fgm==g.field_goals_made)&(g.tpa==g.three_point_field_goals_attempted)&(g.tpm==g.three_point_field_goals_made))
    g['xy_fraction'] = g.xy / g.fga
    game_check = g.groupby('game_id').agg(teams=('team_id','nunique'),all_match=('box_match','all'),min_xy=('xy_fraction','min'))
    candidates = game_check[(game_check.teams==2)&game_check.all_match&(game_check.min_xy>=.95)]
    teams = fg.groupby(['team_id','team_name']).agg(attempts=('made','size'),bounded_locations=('bounded_xy','sum'),games=('game_id','nunique')).reset_index()
    teams['location_fraction']=teams.bounded_locations / teams.attempts
    team_game_counts = g[g.game_id.isin(candidates.index)].groupby('team_id').size()
    teams['candidate_games'] = teams.team_id.map(team_game_counts).fillna(0).astype(int)
    fg['type_value'] = fg.type_text+'_'+fg.score_value.astype(str)
    coverage = fg.groupby('type_value').agg(attempts=('made','size'),located=('bounded_xy','sum'))
    coverage['fraction']=coverage.located/coverage.attempts
    result = {
        'season_ending_year':year,
        'all_shot_rows':len(s),'shot_games':s.game_id.nunique(),'shot_teams':s.team_id.nunique(),
        'free_throw_rows':int(s.type_text.eq('MadeFreeThrow').sum()),
        'ambiguous_fg_type_value_rows':int((fg_type & ~s.score_value.isin([2,3])).sum()),
        'candidate_field_goal_rows':len(fg),'candidate_fg_games':fg.game_id.nunique(),
        'missing_shooter_rows':int(fg.athlete_id_1.isna().sum()),
        'missing_xy_rows':int((~fg.has_xy).sum()),'has_xy_rows':int(fg.has_xy.sum()),
        'bounded_xy_rows':int(fg.bounded_xy.sum()),'bounded_xy_fraction':float(fg.bounded_xy.mean()),
        'sentinel_xy_rows':int(fg.sentinel_xy.sum()),
        'other_out_of_bounds_xy_rows':int((fg.has_xy & ~fg.bounded_xy & ~fg.sentinel_xy).sum()),
        'exact_duplicate_compact_rows':int(s.duplicated().sum()),
        'box_team_games':len(b),'box_games':b.game_id.nunique(),
        'fg_team_games':len(g),'fg_team_games_with_box':int(g._merge.eq('both').sum()),
        'team_games_reconciling_all_four_totals':int(g.box_match.sum()),
        'games_with_two_teams_reconciled_and_95pct_xy_each':len(candidates),
        'candidate_fg_in_those_games':int(fg.game_id.isin(candidates.index).sum()),
        'candidate_teams_at_least_10_games':int((teams.candidate_games>=10).sum()),
        'location_by_shot_type':coverage.reset_index().to_dict(orient='records'),
        'location_by_outcome':fg.groupby('made').bounded_xy.agg(['count','mean']).reset_index().to_dict(orient='records'),
        'box_season_types':b.season_type.value_counts().to_dict(),
        'top_coverage_teams':teams.sort_values(['candidate_games','attempts'],ascending=False).head(20).to_dict(orient='records'),
        'ohio_state':teams[teams.team_name.str.contains('Ohio State',case=False)].to_dict(orient='records'),
        'note':'Candidate field goals before event-ID checks, season-specific D1 membership, geometry certification, and regular-season filtering. Broad coordinate bounds are a diagnostic, not final inclusion rules.'
    }
    (OUT/f'team_coverage_{year}.json').write_text(teams.to_json(orient='records',indent=2))
    (OUT/f'game_reconciliation_{year}.json').write_text(g.drop(columns='_merge').to_json(orient='records',indent=2,date_format='iso'))
    return result

def audit_pbp():
    p=ROOT/'data/raw/play_by_play_2024.parquet'
    cols=['id','game_id','team_id','type_text','score_value','scoring_play','shooting_play','text','coordinate_x_raw','coordinate_y_raw','game_date','season_type']
    d=pd.read_parquet(p,columns=cols)
    shot=d[d.shooting_play.fillna(False)].copy()
    fg=shot[shot.type_text.isin(FG_TYPES)&shot.score_value.isin([2,3])].copy()
    t=fg.text.fillna('')
    return {
        'season':2024,'all_events':len(d),'shot_events':len(shot),'candidate_fg_events':len(fg),
        'missing_event_ids':int(d.id.isna().sum()),
        'duplicate_game_event_keys':int(d.duplicated(['game_id','id']).sum()),
        'duplicate_fg_game_event_keys':int(fg.duplicated(['game_id','id']).sum()),
        'missing_fg_team':int(fg.team_id.isna().sum()),
        'event_text_three_mismatch':int((t.str.contains('three point',case=False)&fg.score_value.ne(3)).sum()),
        'event_text_made_mismatch':int((t.str.contains(' made ',case=False)&~fg.scoring_play).sum()),
        'event_text_missed_mismatch':int((t.str.contains(' missed ',case=False)&fg.scoring_play).sum()),
        'date_min':str(d.game_date.min()),'date_max':str(d.game_date.max()),
        'columns_read':cols,
        'note':'Event text checked only for data integrity; outcome-bearing descriptions must not enter model features.'
    }

def main():
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'seasons':[analyze_season(y) for y in [2023,2024,2025]],'play_by_play_audit':audit_pbp()}
    (OUT/'audit_results.json').write_text(json.dumps(report,indent=2,default=native))
    manifest=[]
    for p in sorted((ROOT/'data/raw').glob('*.parquet')):
        prefix = 'shots' if p.name.startswith('shots') else ('team_boxscores' if p.name.startswith('team_box') else 'pbp')
        manifest.append({'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'url':f'https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_mens_college_basketball_{prefix}/{p.name}'})
    (OUT/'source_manifest.json').write_text(json.dumps({'recorded_utc':report['created_utc'],'files':manifest},indent=2))
    for s in report['seasons']:
        print(json.dumps({k:v for k,v in s.items() if k not in ['location_by_shot_type','top_coverage_teams']},default=native))
    print(json.dumps(report['play_by_play_audit'],default=native))

if __name__=='__main__': main()
