from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if not n:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * np.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / den
    return center - half, center + half


def main() -> None:
    source = ROOT / "data/processed/shots_clean.parquet"
    if not source.exists():
        raise FileNotFoundError("Run scripts/build_clean_table.py first")
    d = pd.read_parquet(source)
    train = d[d.season == 2023].copy()
    test = d[d.season.isin([2024, 2025])].copy()
    overall = train.made.mean()
    zone = train.groupby("shot_zone").agg(attempts=("made", "size"), makes=("made", "sum"), points=("point_value", "sum"))
    zone["make_rate"] = zone.makes / zone.attempts
    zone[["ci_low", "ci_high"]] = [wilson(int(r.makes), int(r.attempts)) for _, r in zone.iterrows()]
    train["observed_points"] = train["point_value"] * train["made"].astype(int)
    zone["expected_points_per_attempt"] = train.groupby("shot_zone")["observed_points"].mean()
    pred = test["shot_zone"].map(zone["make_rate"]).fillna(overall)
    y = test.made.astype(float).to_numpy()
    p = pred.to_numpy()
    brier = float(np.mean((p - y) ** 2))
    logloss = float(-np.mean(y * np.log(np.clip(p, 1e-8, 1 - 1e-8)) + (1 - y) * np.log(np.clip(1 - p, 1e-8, 1 - 1e-8))))
    output = {
        "train_season": 2023,
        "test_seasons": [2024, 2025],
        "train_rows": len(train),
        "test_rows": len(test),
        "overall_train_make_rate": float(overall),
        "zone_baseline_brier": brier,
        "zone_baseline_log_loss": logloss,
        "zone_table": zone.reset_index().to_dict(orient="records"),
    }
    out = ROOT / "data/outputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "zone_baseline.json").write_text(json.dumps(output, indent=2, default=str))
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
