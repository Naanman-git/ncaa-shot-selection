# Shot-level coding guide

## Purpose and scope

This guide defines the fields used by the NCAA Division I men's basketball analysis and the separate prospective validation experiment. One row represents one legally recorded field-goal attempt. Free throws, turnovers before a shot, and possessions without a field-goal attempt are outside the outcome.

The historical study uses public SportsDataverse shot-chart releases. The prospective template uses anonymous participant codes and must not contain names, email addresses, video links, or other direct identifiers.

## Historical analysis fields

| Field | Type and unit | Coding rule |
| --- | --- | --- |
| season | integer | Ending year of the NCAA season. |
| contest_id | text | Stable source game identifier. |
| game_date | date-time | Source game date, stored consistently for chronological history. |
| team_name | text | Source team label used for team-level filtering. |
| player_key | text | Stable mapped identifier within the analysis contract. |
| player_name | text | Public source label for interface filtering; exclude it from anonymous experimental files. |
| shot_x, shot_y | numeric, chart units | Native baseline-relative chart coordinates. Do not infer extra precision. |
| dist_ft | numeric, feet | Euclidean basket distance derived by the upstream adapter. |
| shot_zone | category | Exactly one of `rim`, `paint`, `mid`, `corner3`, or `abovebreak3`. |
| made | binary | `1` for a made field goal and `0` for a missed field goal. |
| point_value | integer | `2` or `3`, determined by the source geometry adapter and aggregate reconciliation. |
| model_p | probability | Frozen model probability for the attempt. Must lie from 0 through 1. |

## Zone definitions

The five zones come from the upstream geometry adapter. They are mutually exclusive labels for recorded chart locations. The `paint` label is a source distance band and should not be treated as a verified painted-key boundary. Point value and zone are checked against aggregate team box scores but are not shot-tracking truth.

## Historical inclusion rules

1. Include NCAA Division I men's games from the stated source seasons.
2. Require both teams in a game to reconcile with ESPN team box totals for field goals and three-pointers.
3. Preserve source multiplicity when the source lacks an event identifier. Do not silently delete exact duplicates.
4. Require valid outcome, coordinate, zone, point-value, team, game, season, and game-date fields.
5. Record every exclusion and source-file hash in the audit output.

## Prospective experiment fields

| Field | Type and unit | Coding rule |
| --- | --- | --- |
| shot_id | text | Unique anonymous attempt identifier. |
| participant_code | text | Anonymous stable code. Never use a player's name or email. |
| session_id | text | Collection session identifier. |
| block_id | text | Randomized or alternated strategy block identifier. |
| block_order | integer | Order of the block within the session, starting at 1. |
| strategy | category | Exactly `current` or `recommended`. |
| attempt_order | integer | Attempt order within the block, starting at 1. |
| shot_x, shot_y | numeric, feet | Coordinates under the frozen court origin and orientation. |
| zone | category | One of the five frozen zones. |
| made | binary | `1` for made and `0` for missed. |
| point_value | integer | `2` or `3` under the chosen NCAA men's ruleset. |
| model_probability | probability | Prediction generated before the outcome is revealed. |
| notes | text | Optional non-identifying protocol deviation note. |

## Quality-control rules

- Freeze the court origin, basket location, orientation, zone definitions, model, recommended distribution, and metrics before collection.
- Randomize or alternate strategy blocks within sessions. Do not collect every current block first and every recommended block later.
- Keep the ball, court, warm-up, participant set, and rest schedule consistent where feasible.
- Record every attempt, including misses and protocol deviations.
- Resolve an error through a dated correction log. Do not overwrite the original observation without an audit trail.
- Store any consent forms or identifying rosters separately from the analytical file.

## Derived quantities

- Observed field-goal percentage equals makes divided by attempts.
- Observed points per attempt equals `made * point_value` averaged across attempts.
- Expected points per attempt equals `model_probability * point_value`.
- Strategy effect equals recommended-strategy observed points per attempt minus current-strategy observed points per attempt.

## Missing data

Required fields must not be missing. A row with an unknown outcome, strategy, point value, or frozen prediction cannot enter the confirmatory analysis. Keep excluded rows in a separate audit file with an exclusion reason.
