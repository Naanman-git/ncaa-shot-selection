# Prospective validation protocol

## Objective

Test two questions after freezing the historical analysis:

1. Do frozen model probabilities agree with outcomes from newly collected attempts?
2. Does the recommended shot distribution change observed points per attempt relative to the current distribution under a controlled collection design?

The historical analysis does not answer the second question. This protocol prepares that experiment without inventing outcomes.

## Preregistration freeze

Before the first validation attempt, record:

- the model file and analysis run identifier;
- coordinate system and five zone definitions;
- current and recommended zone shares;
- shot-availability limits and three-point cap;
- primary metrics and bootstrap method;
- participant population, court, ball, warm-up, rest schedule, and stopping rule.

Save this record with a timestamp and do not change it after observing outcomes. If an operational problem forces a change, document the amendment before continuing.

## Participants and permission

Use anonymous participant codes. Obtain informed permission for practice, video, or individual performance data. Keep the code-to-identity key and consent records outside the analysis folder. Do not publish individual rankings without explicit consent.

## Collection design

Use both strategies within the same sessions when feasible. Randomize the first strategy and then alternate blocks, or generate a balanced random order before the session. This separates strategy from warm-up, fatigue, and learning more effectively than collecting every current-strategy attempt first.

Each block should follow its assigned zone distribution. Record actual locations even when an attempt misses its planned zone. Analyze the attempts actually taken and report adherence to the assigned mix.

The minimum practical design is four sessions with both strategies represented. More sessions provide a more credible cluster bootstrap. The stopping rule should depend on a prespecified attempt target, not on the observed effect.

## Required file

Copy `data/templates/prospective_shots_template.csv` and append one row per attempt. Do not add names or contact information. Generate `model_probability` before revealing the outcome.

## Primary analyses

### Probability validation

- Brier score for all new attempts;
- log loss for all new attempts;
- calibration by probability bin;
- sample size in every reported group.

### Strategy comparison

Let the observed points for an attempt equal `made * point_value`. Report:

- observed points per attempt under each strategy;
- recommended minus current points per attempt;
- a 95% interval from resampling sessions as clusters;
- achieved zone shares and block-order balance.

The primary comparison follows the assigned strategy when the design and adherence records support it. A secondary per-protocol analysis may describe the attempts actually taken, but it must not replace the primary result silently.

## Analysis command

After data collection:

```bash
.venv/bin/python scripts/analyze_prospective_validation.py \
  --input path/to/prospective_shots.csv \
  --output data/outputs/prospective_validation.json
```

The script rejects duplicate attempt IDs, missing required values, invalid probabilities, invalid outcomes, unknown zones, and missing strategy arms.

## Decision language

A positive estimated difference with a wide interval is preliminary evidence. A result supports a strategy only for the studied participants, court, rules, and collection conditions. Opponent response and game-shot availability remain outside a controlled practice experiment.
