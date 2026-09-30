# CourtSense 1.1

## Available features

- Compare two distinct teams within the same season, with shot mix, observed and predicted efficiency, conditional scenario opportunities and supporting sample counts.
- Download a self-contained HTML team report card; browser printing supports a compact A4 handout or Save as PDF.
- Inspect per-zone sample support, fixed-mix game-bootstrap intervals, stricter scenario limits and separate historical season scenarios. Support labels are descriptive thresholds, not statistical confidence levels.
- Inspect a player's game-by-game season, weighted recent-five-game trend, shot map and video-review prompts. No causal training benefit is claimed.
- Follow six interactive story chapters using the selected team/player and download speaking notes.
- Explore home/away source designations and points per estimated possession from reconciled team box scores.
- See application, protocol and analysis dates; draft and download feedback without a GitHub account. The issue tracker itself is private and requires collaborator access.

## Data and attribution

SportsDataverse publishes NCAA-native shots and ESPN-origin box scores:
https://github.com/sportsdataverse/sportsdataverse-data/releases

The hoopR.mbb producer explicitly describes data, code and documentation as CC BY 4.0:
https://github.com/sportsdataverse/hoopR-mbb-data/blob/main/LICENSE.md
License: https://creativecommons.org/licenses/by/4.0/
Credit: SportsDataverse / hoopR.mbb authors. CourtSense filters, reconciles and aggregates box-score records; no endorsement is implied.

The central release-store MIT license covers software; it is not independently treated as proof that every underlying NCAA/ESPN asset is freely redistributable. Existing source access and hashes remain documented in research/source_manifest.json. Recheck source terms before commercial distribution or broad raw-data redistribution; this release adds only derived box-score aggregates.

The possession estimate follows FGA − OR + total TO + 0.475 × FTA for each team, averaging both teams in each game. Team rates are ratios of total points to total estimated possessions, unadjusted for opponents. This differs from averaging per-game rates in some published rating systems.
Method: https://kenpom.com/blog/ratings-glossary/

The build requires both team boxes, matching shot attempt/make and three-point counts, and agreement between field-goal-plus-free-throw points and team score. Missing or invalid possession inputs exclude the pair. The context manifest records counts and input hashes.

## Honest limits

- Home/away is a source designation, not verified venue or neutral-site status.
- Possessions are estimated, not exact play-sequence reconstruction. Second-chance sequences and exact possession outcomes are not available in this view.
- Defender distance, shot-clock pressure, fatigue, assisted status and play type cannot reliably be joined to the native shots. The native source has no stable event key and unreliable period/time fields; no invented joins or predictor values are introduced.
- Final game score is not used as a predictor of earlier shots.
- Most source player IDs appear in only one season. Automatic name-based cross-season matching is unsafe; player development stays within a selected season.
- Historical model results remain frozen. The new views do not retrain or reselect the model, and predictions on training seasons are identified as in-sample.
- The prospective experiment is excluded at the user's request.

## Maintenance

GitHub quality checks run tests, exercise the app and validate the snapshot on pushes/PRs. A validated snapshot is retained for seven days as a build artifact. A separate readiness check follows successful main-branch push checks and can be run manually. It only accepts an actual `ok` health response; sleep/sign-in/HTML pages are not reported healthy. It does not promise continuous uptime or verify visible UI. GitHub notification delivery depends on account settings.

For a controlled local rebuild, after producing and reviewing analysis outputs:

```bash
PYTHONPATH=src .venv/bin/python scripts/stage_snapshot.py
```

This creates a unique staging folder under tmp and checks it without replacing hosted data. Review results, source permissions and any protocol change before deliberately promoting those files. On Cloud, restart the app after module changes if an existing server keeps old imported chart code in memory.

The report and slide deck remain the frozen research deliverables. New portfolio functionality is documented here rather than rewriting the academic evidence.
