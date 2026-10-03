# Beginner's guide coverage and maintenance

The guide explains specialized words and phrases in the interface and files, including acronyms, statistical language and confusing basketball concepts. Ordinary navigation words are explained in the tour or file-format topics when useful. It is a reviewed reference, with no external chatbot service or generated answers.

## Coverage by page

| Page or area | Covered concepts |
| --- | --- |
| Filters and summary | NCAA, Division I, season ending years, team/player scope, attempts/FGA, makes/FGM, FG%, observed/predicted, rates and units |
| Court explorer | Probability, PPS, expected points, shares, cells, legends, map minimum, coordinates, distance, angle, all five source zones and geometry caveats |
| Shot-mix scenarios | Mix, pp, zone limits, L1 movement, three-point cap, uncertainty penalty, shrinkage, pooled priors, EP, gains, eligibility, feasibility, fixed-mix intervals and opportunity assumptions |
| Evidence diagnostics | Limited/usable/broader support, distinct games, bootstrap/clusters, bounds, SD, sensitivity, season stability and causal limits |
| Compare teams | Independent controls, descriptive comparisons, default scenario limits, report cards, in-sample cautions and support |
| Player development | Profile selection, game trends, weighted five-game windows, observed-minus-predicted gaps, source identity limits and review prompts |
| Team context | Box scores/reconciliation, possessions and formula, PPP, FT/FTM/FTA, TO/TOV, OR/ORB, team-games, source designation and neutral sites |
| Model validation | Independent evaluation season, mean Brier/log loss with separate formulas, calibration, baselines, chronological splits, leakage, features, splines, history, coefficients, odds, L2 and H1–H4 |
| Methods | Coverage/missingness, unavailable context, source attribution, joins, IDs, audit, snapshot/version, UTC, SHA-256, settings, seeds, reproducibility and prospective status |
| Downloads | CSV/JSON/PDF/PPTX/HTML, raw field names, anonymous participant/shot/session/block codes, strategy values, order, feedback and CC BY 4.0 |

## Contextual examples

`GuideContext` is assembled after all page controls render, so a new evaluation-season or profile choice is reflected immediately. The main shot selection, full evaluation sample, whole-team context and independently selected profile are explicitly labeled. Unavailable or infeasible scenarios do not display a scoring gain. Definitions and their offline download come from one catalog.

## Checks

- `tests/test_guide.py` checks common queries and misspellings, short acronyms, unknown queries, units and changes in contextual examples.
- Its coverage check reads the actual tracked shot/context schemas, prospective template, analysis JSON keys and displayed numeric/boolean table labels. A new field requires a documented alias.
- `scripts/smoke_app.py` exercises the rendered guide, related navigation, clear/quick buttons, unmatched search, evaluation-season updates and season/team changes using Streamlit AppTest.
- The committed offline guide must match `guide_markdown()`. Regenerate it after changing the catalog: `PYTHONPATH=src .venv/bin/python -c "from pathlib import Path; from ncaa_shot_selection.guide import guide_markdown; Path('docs/BEGINNER_GUIDE.md').write_text(guide_markdown())"`.
- Browser review checks readable layout, expansion, download and the collapsed sidebar on desktop and a narrow viewport.

## Source-specific interpretation

Native point values and zones are inferred upstream from chart geometry and checked against aggregate box scores; they are not verified tracking truth. The source's Paint grouping is a distance band, not a confirmed painted-lane boundary. The current native builder retains exact matching rows because an event identifier is unavailable. The saved analysis audit contains inherited metadata from an earlier cleaning stage, including duplicate-removal counters; use the current snapshot season summary for the displayed cohort, and do not infer its duplicate policy from those legacy counters.

The guide explains these distinctions without modifying the frozen data, fitted model, historical results or prospective experiment status.
