# Hypotheses and statistical tests

The analysis freezes the following hypotheses before interpreting the final 2025-26 season. The generated `final_results.json` stores the result and decision for each hypothesis.

## H1: Distance and make probability

Predicted make probability decreases as shot distance increases. The check uses the frozen model's average prediction within prespecified distance bands on the untouched final season and reports the Spearman association between band distance and predicted make probability. The spline model remains nonlinear, so this test evaluates the overall pattern rather than assuming a constant distance effect.

## H2: Accuracy and expected value

A lower-probability three-point zone can produce higher expected points per attempt than a two-point zone. The confirmatory comparison uses held-out corner-three and paint averages. This is an expected-value comparison, not a claim that every available three-point attempt should replace a paint attempt.

## H3: Small-sample shrinkage

Raw zone rates move toward pooled training estimates after adding the fixed 30-attempt prior. The prespecified Ohio State case study reports raw and shrunk rates together. Shrinkage reduces the influence of small samples without pretending that the prior removes all uncertainty.

## H4: Model value beyond a zone baseline

The selected spatial and prior-history model improves held-out probability prediction over the zone-shrinkage baseline. The comparison uses final-season Brier score and log loss after model selection is frozen. A smaller score indicates better probability predictions.

## Interpretation rules

- Use `supported`, `mixed`, or `not supported` rather than treating a threshold as proof.
- Preserve effect size, direction, population, and held-out sample size.
- Do not convert retrospective predictive evidence into a causal strategy claim.
- Treat the prospective strategy comparison as a separate experiment.
