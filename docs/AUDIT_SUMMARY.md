# Data audit summary

Native NCAA rows are retained at source multiplicity; exact duplicate rows are not removed because no event key is supplied. Each candidate game/team is reconciled against ESPN field-goal attempts, makes, three-point attempts and makes. The final cohort requires both teams to pass that check. Coordinates are complete for the native rows used here, but the upstream zone and point-value fields are derived from chart geometry. They support recorded-location analysis and aggregate reconciliation, not a claim of shot-tracking precision.

The final run identifier, source hash, per-season included counts, reconciliation evidence and limitations are recorded in `data/outputs/final_results.json`. Audit files under `research/` preserve the upstream source and coverage checks.
