#!/usr/bin/env python3
"""Validate and analyze a post-freeze shot-selection experiment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss

STRATEGIES = {"current", "recommended"}
ZONES = {"rim", "paint", "mid", "corner3", "abovebreak3"}
REQUIRED = [
    "shot_id", "participant_code", "session_id", "block_id", "block_order",
    "strategy", "attempt_order", "shot_x", "shot_y", "zone", "made",
    "point_value", "model_probability",
]


def validate(frame: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(set(REQUIRED) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    data = frame.copy()
    if data.empty:
        raise ValueError("The prospective file contains no attempts")
    if data[REQUIRED].isna().any().any():
        bad = data[REQUIRED].columns[data[REQUIRED].isna().any()].tolist()
        raise ValueError(f"Required values are missing in: {', '.join(bad)}")
    if data.shot_id.astype(str).duplicated().any():
        raise ValueError("shot_id values must be unique")
    if set(data.strategy.astype(str)) != STRATEGIES:
        raise ValueError("strategy must contain both current and recommended attempts")
    if not set(data.zone.astype(str)).issubset(ZONES):
        raise ValueError("zone contains a value outside the frozen five-zone definition")
    for column in ["block_order", "attempt_order", "shot_x", "shot_y", "made",
                   "point_value", "model_probability"]:
        data[column] = pd.to_numeric(data[column], errors="raise")
    if not data.made.isin([0, 1]).all():
        raise ValueError("made must be coded 0 or 1")
    if not data.point_value.isin([2, 3]).all():
        raise ValueError("point_value must be 2 or 3")
    if not data.model_probability.between(0, 1, inclusive="both").all():
        raise ValueError("model_probability must lie from 0 through 1")
    if (data[["block_order", "attempt_order"]] < 1).any().any():
        raise ValueError("block_order and attempt_order must start at 1")
    data["observed_points"] = data.made * data.point_value
    return data


def calibration(data: pd.DataFrame, bins: int = 10) -> list[dict]:
    bucket = np.minimum((data.model_probability.to_numpy() * bins).astype(int), bins - 1)
    rows = []
    for number in range(bins):
        mask = bucket == number
        if mask.any():
            rows.append({
                "bin": number,
                "attempts": int(mask.sum()),
                "mean_predicted": float(data.loc[mask, "model_probability"].mean()),
                "observed_fg": float(data.loc[mask, "made"].mean()),
            })
    return rows


def cluster_bootstrap_difference(data: pd.DataFrame, repeats: int, seed: int) -> dict:
    sessions = list(data.session_id.astype(str).unique())
    if len(sessions) < 2:
        raise ValueError("At least two sessions are required for a session-cluster interval")
    grouped = {key: value for key, value in data.groupby(data.session_id.astype(str))}
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(repeats):
        sample = pd.concat([grouped[key] for key in rng.choice(sessions, len(sessions), replace=True)],
                           ignore_index=True)
        means = sample.groupby("strategy").observed_points.mean()
        if STRATEGIES.issubset(means.index):
            values.append(float(means["recommended"] - means["current"]))
    if not values:
        raise ValueError("Bootstrap samples did not contain both strategy arms")
    return {
        "low": float(np.quantile(values, 0.025)),
        "high": float(np.quantile(values, 0.975)),
        "repeats": int(repeats),
        "cluster": "session_id",
    }


def analyze(frame: pd.DataFrame, *, repeats: int = 2000, seed: int = 42) -> dict:
    data = validate(frame)
    probability = np.clip(data.model_probability.to_numpy(float), 1e-9, 1 - 1e-9)
    strategy = (data.groupby("strategy", observed=True)
        .agg(attempts=("made", "size"), observed_fg=("made", "mean"),
             observed_points_per_attempt=("observed_points", "mean"))
        .reset_index())
    means = strategy.set_index("strategy").observed_points_per_attempt
    difference = float(means["recommended"] - means["current"])
    zone_mix = (data.groupby(["strategy", "zone"], observed=True).size()
        .rename("attempts").reset_index())
    zone_mix["share"] = zone_mix.attempts / zone_mix.groupby("strategy").attempts.transform("sum")
    order = (data.groupby(["strategy", "block_order"], observed=True).size()
        .rename("attempts").reset_index())
    return {
        "attempts": int(len(data)),
        "participants": int(data.participant_code.nunique()),
        "sessions": int(data.session_id.nunique()),
        "probability_validation": {
            "brier": float(brier_score_loss(data.made, probability)),
            "log_loss": float(log_loss(data.made, probability, labels=[0, 1])),
            "calibration": calibration(data),
        },
        "strategy_results": strategy.to_dict("records"),
        "recommended_minus_current_points_per_attempt": difference,
        "recommended_minus_current_points_per_100_attempts": 100 * difference,
        "strategy_interval": cluster_bootstrap_difference(data, repeats, seed),
        "achieved_zone_mix": zone_mix.to_dict("records"),
        "block_order_balance": order.to_dict("records"),
        "interpretation": (
            "This result applies to the collected participants and protocol. It does not measure "
            "opponent response or guarantee the same effect in games."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bootstrap-repeats", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    results = analyze(pd.read_csv(args.input), repeats=args.bootstrap_repeats, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
