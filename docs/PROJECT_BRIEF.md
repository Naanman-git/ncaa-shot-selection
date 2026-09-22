# Project brief

## Goal

Deliver a Division I men’s NCAA basketball shot-selection study that works as both an academic submission and a portfolio product. It asks how make probability varies over recorded shot locations, and how a modest constrained change in a team’s recorded shot mix changes conditional points per recorded field-goal attempt.

## Frozen design

- Native SportsDataverse shot files: seasons ending 2023–2026.
- ESPN team boxes: coverage and game/team count reconciliation only.
- Training: 2023 and 2024; model selection: 2025; final test: 2026.
- Selected estimator: L2 logistic regression with zone, distance spline, angle and prior-day player-zone history.
- Scenario: 30-attempt shrinkage, ±5 percentage-point zone limit, L1 movement budget 0.20, three-point cap 60%, game bootstrap.

## Deliverables

`data/outputs/final_results.json` is the single evidence contract. The report, editable deck and Streamlit explorer consume it. The report and deck label geometry-inferred zone/value fields, coverage limits, conditional scenario assumptions and non-causal interpretation.
