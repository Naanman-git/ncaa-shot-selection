import pandas as pd
import pytest
from ncaa_shot_selection.insights import game_trend, points_interval, possession_estimates, report_card, zone_evidence


def shots():
    return pd.DataFrame([dict(contest_id=str(g),game_date=f'2026-01-{g+1:02d}',made=int(i%2==0),
                             point_value=2,shot_zone='rim',model_p=.5) for g in range(6) for i in range(20)])


def test_rolling_rate_weights_attempts():
    f=shots().iloc[:21].copy()
    f.loc[f.contest_id=='0','made']=1
    f.loc[f.contest_id=='1','made']=0
    trend=game_trend(f)
    assert trend.iloc[-1]['Recent 5 games · observed']==pytest.approx(40/21)
    assert points_interval(f) is None


def test_support_requires_games_as_well_as_shots():
    f=shots()
    assert zone_evidence(f).iloc[0].support=='Usable sample'
    f['contest_id']='one'
    assert zone_evidence(f).iloc[0].support=='Limited sample'


def test_bootstrap_reproducible_with_constant_rate():
    assert points_interval(shots())==(1.,1.)
    assert points_interval(shots(),seed=5)==points_interval(shots(),seed=5)


def boxes():
    return pd.DataFrame([
        dict(season=2026,game_id='1',team_id='A',field_goals_attempted=60,free_throws_attempted=20,offensive_rebounds=10,total_turnovers=12,team_score=80),
        dict(season=2026,game_id='1',team_id='B',field_goals_attempted=55,free_throws_attempted=20,offensive_rebounds=5,total_turnovers=14,team_score=72)])


def test_possessions_pair_teams_and_use_total_turnovers_once():
    b=possession_estimates(boxes())
    assert b.estimated_possessions.tolist()==[72.5,72.5]
    with pytest.raises(ValueError,match='Duplicate'):
        possession_estimates(pd.concat([boxes(),boxes()]))


def test_bad_box_or_missing_opponent_excludes_entire_game():
    b=boxes(); b.loc[0,'total_turnovers']=None
    assert possession_estimates(b).empty
    assert possession_estimates(boxes().iloc[:1]).empty


def test_report_escapes_labels_and_handles_unavailable_scenario():
    result=report_card('<script>alert(1)</script>',2026,shots(),{'feasible':False},{'run_id':'test'})
    assert '<script>' not in result
    assert '&lt;script&gt;' in result
    assert 'No feasible scenario' in result
    assert '120' in result
