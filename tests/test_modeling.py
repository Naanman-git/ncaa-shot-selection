import numpy as np
import pandas as pd
from ncaa_shot_selection.modeling import add_history


def fixture():
    return pd.DataFrame({"season":[2025]*5,"player_key":["A"]*5,
        "shot_zone":["rim"]*5,"game_date":["2025-01-01"]*2+["2025-01-02"]*2+["2025-01-03"],
        "made":[True,False,True,True,False],"shot_x":[0]*5,"shot_y":[1]*5})


def test_no_current_day_or_future_outcome_leaks():
    d=fixture()
    a=add_history(d)
    altered=d.copy()
    altered.loc[2:,"made"]=False
    b=add_history(altered)
    np.testing.assert_array_equal(a.history_logit.iloc[:4],b.history_logit.iloc[:4])
    assert a.prior_attempts.tolist()==[0,0,2,2,4]
    assert a.prior_makes.tolist()==[0,0,1,1,3]


def test_history_does_not_cross_player_or_season():
    d=fixture()
    d.loc[3,"player_key"]="B"
    d.loc[4,"season"]=2026
    a=add_history(d)
    assert a.loc[3,"prior_attempts"]==0
    assert a.loc[4,"prior_attempts"]==0
