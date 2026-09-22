import numpy as np
from ncaa_shot_selection.optimization import solve_mix


def test_bounds_budget_and_support():
    current=np.array([.30,.15,.20,.10,.25])
    r=solve_mix(current,[1.3,.8,.7,1.1,1.05],[True,True,False,True,True])
    assert r["feasible"]
    q=r["share"]
    assert np.isclose(q.sum(),1)
    assert np.abs(q-current).max()<=.0500001
    assert np.abs(q-current).sum()<=.2000001
    assert q[2]==current[2]
    assert q[3:].sum()<=.6000001


def test_infeasible_cap_is_explicit_not_relaxed():
    r=solve_mix([.1,.05,.05,.3,.5],[1]*5,[True]*5,max_shift=.01,three_cap=.5)
    assert not r["feasible"]


def test_zero_shift_returns_baseline():
    c=np.array([.3,.2,.2,.1,.2])
    r=solve_mix(c,[1,2,3,4,5],[True]*5,max_shift=0)
    np.testing.assert_allclose(r["share"],c)
