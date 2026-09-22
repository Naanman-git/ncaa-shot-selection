"""Transparent constrained, descriptive shot-mix scenarios."""
from __future__ import annotations
import numpy as np
from scipy.optimize import linprog


def solve_mix(current, values, eligible, *, max_shift=.05, budget=.20, three_cap=.60):
    """L1 budget .20 moves at most 10% of attempts. Unsupported zones stay fixed."""
    current, values = np.asarray(current, float), np.asarray(values, float)
    eligible = np.asarray(eligible, bool)
    k = len(current)
    if k != 5 or values.shape != current.shape or eligible.shape != current.shape:
        raise ValueError("Expected the five ordered zones")
    if not np.isfinite(current).all() or not np.isfinite(values).all():
        raise ValueError("Shares and values must be finite")
    if (current < 0).any() or not np.isclose(current.sum(), 1):
        raise ValueError("Current shares must be nonnegative and sum to one")
    if not 0 <= max_shift <= 1 or not 0 <= budget <= 2 or not 0 <= three_cap <= 1:
        raise ValueError("Invalid constraint range")
    bounds = [(max(0, q-max_shift), min(1, q+max_shift)) if ok else (q, q)
              for q, ok in zip(current, eligible)] + [(0, None)]*k
    a = np.vstack([np.c_[np.eye(k), -np.eye(k)],
                   np.c_[-np.eye(k), -np.eye(k)],
                   np.r_[np.zeros(k), np.ones(k)],
                   np.r_[0, 0, 0, 1, 1, np.zeros(k)]])
    b = np.r_[current, -current, budget, three_cap]
    result = linprog(np.r_[-values, np.zeros(k)], A_ub=a, b_ub=b,
                     A_eq=[np.r_[np.ones(k), np.zeros(k)]], b_eq=[1.],
                     bounds=bounds, method="highs")
    return {"feasible": bool(result.success),
            "share": result.x[:k] if result.success else current.copy(),
            "message": "Solved within all stated constraints." if result.success else
                "No feasible mix satisfies these limits. Increase the three-point cap or movement allowance."}
