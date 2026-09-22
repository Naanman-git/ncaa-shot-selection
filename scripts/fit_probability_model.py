"""Fit the first auditable probability model and evaluate chronological holdouts."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["shot_zone", "point_value", "dist_ft"]


def calibration(y: np.ndarray, p: np.ndarray, bins: int = 10) -> list[dict]:
    edges = np.linspace(0, 1, bins + 1)
    group = np.clip(np.digitize(p, edges[1:-1], right=False), 0, bins - 1)
    result = []
    for i in range(bins):
        mask = group == i
        if mask.any():
            result.append({"bin": i, "n": int(mask.sum()), "mean_predicted": float(p[mask].mean()), "observed_rate": float(y[mask].mean())})
    return result


def evaluate(model: Pipeline, data: pd.DataFrame, label: str) -> dict:
    y = data.made.astype(int).to_numpy()
    p = model.predict_proba(data[FEATURES])[:, 1]
    return {
        "label": label,
        "rows": len(data),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "calibration": calibration(y, p),
    }


def main() -> None:
    data = pd.read_parquet(ROOT / "data/processed/shots_clean.parquet")
    train = data[data.season == 2023].copy()
    valid = data[data.season == 2024].copy()
    test = data[data.season == 2025].copy()
    pre = ColumnTransformer(
        [("zone", OneHotEncoder(handle_unknown="ignore"), ["shot_zone"]),
         ("numeric", StandardScaler(), ["point_value", "dist_ft"])],
        remainder="drop",
    )
    model = Pipeline([("preprocess", pre), ("logistic", LogisticRegression(max_iter=200, C=1.0, solver="lbfgs"))])
    model.fit(train[FEATURES], train.made.astype(int))
    metrics = {
        "model": "logistic_regression_zone_distance_value",
        "training_season": 2023,
        "validation_season": 2024,
        "test_season": 2025,
        "features": FEATURES,
        "evaluation": [evaluate(model, train, "train_2023"), evaluate(model, valid, "validation_2024"), evaluate(model, test, "test_2025")],
        "coefficients": model.named_steps["logistic"].coef_.ravel().tolist(),
        "intercept": model.named_steps["logistic"].intercept_.tolist(),
        "classes": model.named_steps["logistic"].classes_.tolist(),
    }
    out = ROOT / "data/outputs"
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out / "probability_model.joblib")
    (out / "probability_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
