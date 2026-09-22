"""Chronological probability modeling with strictly prior-day player history."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, SplineTransformer

ZONES = ["rim", "paint", "mid", "corner3", "abovebreak3"]
PRIOR = dict(zip(ZONES, [.60, .40, .36, .35, .34]))


def add_history(data: pd.DataFrame) -> pd.DataFrame:
    """Earlier days only; seasons reset; shots on a date share history.

    Fixed weak priors use no held-out outcomes. This retrospective online test
    permits results from earlier test dates, never the current/future date.
    """
    d = data.copy()
    d["game_day"] = pd.to_datetime(d.game_date, utc=True).dt.floor("D")
    if d.game_day.isna().any():
        raise ValueError("Chronological history requires complete game dates")
    keys = ["season", "player_key", "shot_zone", "game_day"]
    grouped = d.groupby(keys, observed=True, dropna=False).made.agg(["sum", "count"]).reset_index()
    grouped = grouped.sort_values(keys)
    by = grouped.groupby(keys[:-1], observed=True, dropna=False)
    grouped["prior_makes"] = by["sum"].cumsum() - grouped["sum"]
    grouped["prior_attempts"] = by["count"].cumsum() - grouped["count"]
    d = d.merge(grouped[keys+["prior_makes", "prior_attempts"]], on=keys,
                how="left", validate="many_to_one", sort=False)
    prior = d.shot_zone.astype(str).map(PRIOR).astype(float)
    p = (d.prior_makes + 30*prior)/(d.prior_attempts+30)
    d["history_logit"] = np.log(p/(1-p))
    d["history_size"] = np.log1p(d.prior_attempts)
    d["abs_angle"] = np.arctan2(d.shot_x.abs(), d.shot_y.clip(lower=.01))
    return d


def make_model(history=False):
    transforms = [
        ("zone", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["shot_zone"]),
        ("distance", SplineTransformer(n_knots=5, degree=3, include_bias=False,
                                        extrapolation="constant"), ["dist_ft"]),
        ("angle", StandardScaler(), ["abs_angle"]),
    ]
    if history:
        transforms.append(("history", StandardScaler(), ["history_logit", "history_size"]))
    return Pipeline([("features", ColumnTransformer(transforms)),
                     ("model", LogisticRegression(C=1.0, max_iter=300, solver="lbfgs"))])


def calibration(y, p, bins=10):
    y, p = np.asarray(y), np.asarray(p)
    bucket = np.clip((p*bins).astype(int), 0, bins-1)
    return [{"bin": i, "n": int((bucket==i).sum()),
             "mean_predicted": float(p[bucket==i].mean()),
             "observed": float(y[bucket==i].mean())}
            for i in range(bins) if (bucket==i).any()]


def game_bootstrap_metrics(data, p, baseline_p, seed=42, repeats=500):
    y = data.made.to_numpy(float)
    p = np.clip(p, 1e-9, 1-1e-9)
    base = np.asarray(baseline_p)
    errors = pd.DataFrame({"game": data.contest_id.to_numpy(), "n": 1,
        "brier": (y-p)**2, "log_loss": -(y*np.log(p)+(1-y)*np.log(1-p)),
        "brier_difference": (y-p)**2-(y-base)**2}).groupby("game").sum()
    a = errors.to_numpy(float)
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(repeats):
        sums = a[rng.integers(0, len(a), len(a))].sum(axis=0)
        results.append(sums[1:]/sums[0])
    samples = np.asarray(results)
    return {name: {"low": float(np.quantile(samples[:, i], .025)),
                   "high": float(np.quantile(samples[:, i], .975))}
            for i, name in enumerate(errors.columns[1:])}
