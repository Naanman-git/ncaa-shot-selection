# CourtSense beginner's guide

100 explanations of the interface and downloadable field names.

The interactive guide also shows examples from your current selection. This download contains general explanations and worked examples, not live-filtered values.

## Start & basketball basics

### Start here: what CourtSense does

CourtSense helps you explore where college basketball teams shoot, how often those shots go in, and what a limited change in their shot mix could mean.

**Example:** Choose a season and team, then read the five summary cards and the three court maps. Use Model validation to see how well the probabilities worked on later shots.

**More detail:** Use Choose your view in this sidebar to change the season, team or player. Court explorer describes that selection. Shot-mix scenarios explores a conditional change. Compare teams has its own two team choices; Player development has its own profile choice. Team context describes the whole team. Model validation has an independent evaluation-season choice. Methods & downloads explains the evidence and provides reports. The sidebar arrow closes this guide; the top-left arrow opens it again.

**Also called / searchable fields:** CourtSense; beginner; first visit; tour; how to use; dashboard; board

**Related:** Selection, scope and filters; Observed versus predicted; Scenario, retrospective and conditional estimate; Model validation and evaluation season

### NCAA and Division I (D1)

NCAA stands for National Collegiate Athletic Association. Division I is one of its competition divisions. This project covers Division I men's college basketball.

**Example:** An NBA game or a women's college game is outside this project's population, even if a similar-looking shot map is available elsewhere.

**More detail:** A population is the group the research is about. Conclusions depend on the rules, players and available games in that group. The project checks Division I membership and source coverage; it does not claim that every Division I game is included. NCAA court rules and the source's coordinates determine how locations should be interpreted.

**Also called / searchable fields:** NCAA; National Collegiate Athletic Association; Division I; D1; DI; men's basketball; college basketball

**Related:** Coverage, missing data and limitations; Zones and the zone breakdown

### Season and ending-year codes

A basketball season spans two calendar years. The source stores the year in which the season ends.

**Example:** A row with season = 2026 belongs to 2025–26, not 2026–27. The displayed label translates this code for you.

**More detail:** Changing Season changes the available teams, players and shots. date_start and date_end in the saved results describe the earliest and latest included dates, not guaranteed official season boundaries. The evaluation season in Model validation is a separate control. Source player IDs often change across seasons, so the app does not automatically join the same name across years.

**Also called / searchable fields:** season; 2023; 2024; 2025; 2026; date_start; date_end; date range

**Related:** Selection, scope and filters; ID, player keys and game identifiers; Training, model selection, held-out and final test

### Selection, scope and filters

A filter chooses which records are included in a view. The selection shown below the title tells you whose field-goal attempts are in the top summary cards and court maps.

**Example:** Ohio State + All players means the team's available attempts. Selecting one player narrows those cards, maps and the main scenario to that player's attempts.

**More detail:** Compare teams uses the First team and Second team controls. Player development uses Player profile. Team context always uses the whole selected team, even when a sidebar player is selected. Model validation uses its own Evaluation season and the complete evaluation dataset. Read each page's selection before comparing numbers. A total can differ between pages because they deliberately describe different groups.

**Also called / searchable fields:** Choose your view; selection; scope; filter; team; team_name; player; player_name; all players; all Division I teams; First team; Second team; Player profile

**Related:** Start here: what CourtSense does; Team-games versus games; Model validation and evaluation season

### Attempts / FGA: shots tried

A field-goal attempt is one recorded two-point or three-point shot, whether it goes in or misses. FGA means field-goal attempts. Free throws are counted separately.

**Example:** Trying 12 two-pointers and 8 three-pointers gives 20 field-goal attempts. Making or missing does not change that attempt count.

**More detail:** The court's frequency map counts attempts at each location. count, attempts and sometimes n are exported count labels; n on the validation page is the number of evaluated shots. A shot-file row represents one attempt. Counts describe available records, so incomplete source coverage can leave out real attempts. Attempts outside the displayed half-court still count in the main totals.

**Also called / searchable fields:** attempt; attempts; recorded attempts; count; n; FGA; field-goal attempts; evaluated attempts; rows; shots attempted; frequency

**Related:** Makes / FGM: shots that went in; Coverage, missing data and limitations; Court map, heatmap, cells and color scale

### Makes / FGM: shots that went in

A make is a successful field-goal attempt. FGM means field goals made. The shot-file field made uses 1 for a make and 0 for a miss.

**Example:** In [1, 0, 1, 0, 0], two of the five attempts were made. This is 2 ÷ 5 = 40% shooting.

**More detail:** This 0/1 coding lets the model learn a probability of success. Averaging made gives the make rate. Both a made two-pointer and a made three-pointer contribute one make; their point values differ. Free throws made, FTM, belong to Team context and are not included in the field-goal make count.

**Also called / searchable fields:** made; makes; shots made; FGM; field goals made; binary outcome; make_rate

**Related:** FG% / fg_pct: field-goal percentage; Point value: two or three points; FT / FTM: free throws made and free-throw points

### FG% / fg_pct: field-goal percentage

Field-goal percentage is the share of attempted field goals that went in: makes divided by attempts. It describes what actually happened.

**Example:** 45 makes from 100 attempts gives 45%. An exported decimal of 0.45 means 45%, not 0.45%. A rise from 40% to 45% is five percentage points.

**More detail:** FG stands for field goal. fg_pct and raw_fg name the same basic unadjusted rate in different tables. A two-pointer and a three-pointer each count as one attempt in FG%. A team can have a lower FG% but score more points per attempt by taking more threes. FG% does not include free throws or show how difficult the attempts were.

**Also called / searchable fields:** FG%; FG pct; fg_pct; field-goal %; field goal percentage; observed FG%; observed field-goal %; raw_fg; recorded make rate; observed_fg

**Related:** PPS: observed points per attempt; Percentage points (pp) versus percent change; Adjusted make rate, shrinkage and shrunk_fg

### Point value: two or three points

A recorded field-goal attempt is worth either two or three points if made. A miss scores zero points on that attempt.

**Example:** A made three scores 1 × 3 = 3 points; a missed three scores 0 × 3 = 0. A 40% make probability gives 0.40 × 3 = 1.20 expected points.

**More detail:** For these NCAA-native files, the upstream adapter infers point value from chart geometry; the project checks aggregate two- and three-point counts against box scores. It is not verified shot-level tracking truth. CourtSense keeps that recorded value instead of reassigning it from the displayed court drawing. expected_value_if_made describes the scoring value conditional on a make, not a prediction that the shot will be made.

**Also called / searchable fields:** point_value; shot value; two-pointer; two pointer; three-pointer; three pointer; 2P; 3P; two-point; three-point; expected_value_if_made

**Related:** Make probability: chance of a successful shot; Zones and the zone breakdown; Reconciliation and joining shot data to box scores

### Observed versus predicted

Observed means what happened in the recorded data. Predicted means what the model estimated would happen, expressed as an average or a probability.

**Example:** A player may actually score 1.10 points per attempt while the model predicted 1.04 for those same attempts. The two numbers answer different questions.

**More detail:** Observed results vary with luck, shot difficulty and the available sample. Predicted results depend on the information supplied to the model and its assumptions. Agreement in an overall average does not prove accurate predictions for every player or location. Use calibration and evaluation scores to check probability quality on later shots.

**Also called / searchable fields:** observed; recorded; actual; predicted; prediction; estimate; model estimate; what happened

**Related:** Make probability: chance of a successful shot; Observed-minus-predicted gap; Probability calibration and the diagonal

## Court explorer

### Make probability: chance of a successful shot

Make probability is the model's estimated chance that an attempt goes in. It lies between 0 and 1, or between 0% and 100%.

**Example:** A probability of 0.40 means 40%. Across many comparable shots with good calibration, about 40 out of 100 should go in. It does not decide the next shot's result.

**More detail:** The model uses zone, distance, angle and earlier player shooting history. The map averages predictions at recorded locations; it does not simulate an unseen shot at every blank square. A 0.60 prediction followed by a miss is possible and does not by itself disprove the model. model_p and model_probability are probability field names, not observed percentages.

**Also called / searchable fields:** make probability; probability; model_p; model_probability; predicted_fg; chance of a make; likelihood; how often they fall; average predicted make probability

**Related:** Predicted points per attempt / expected_pps; Probability calibration and the diagonal; Earlier player history and history size

### PPS: observed points per attempt

Observed points per attempt is actual field-goal points divided by field-goal attempts. PPS means points per shot in this project.

**Example:** If 100 attempts produce 110 field-goal points, the rate is 110 ÷ 100 = 1.10 points per attempt. It averages makes and misses together.

**More detail:** For each shot, observed points = made × point_value. Add those points and divide by the number of attempts. This measure accounts for threes being worth more than twos. It excludes free throws, turnovers, rebounds and passing opportunities, so it is not a whole-offense points-per-possession measure. Do not interpret 1.10 as a 110% chance of making a shot.

**Also called / searchable fields:** PPS; pps; points per shot; points/attempt; observed_pps; observed points / attempt; Observed pts / attempt; pts/att; observed points; points scored

**Related:** Predicted points per attempt / expected_pps; Points per estimated possession / PPP; Point value: two or three points

### Predicted points per attempt / expected_pps

Predicted points per attempt averages the model's make probability multiplied by each shot's scoring value. It is a long-run average under the model.

**Example:** A three-pointer with a 40% chance gives 0.40 × 3 = 1.20 expected points. A two-pointer with a 50% chance gives 0.50 × 2 = 1.00.

**More detail:** A single attempt still scores zero, two or three field-goal points. The decimal expresses an average over repeated opportunities, not a fractional basket. The top cards and court maps use the frozen predictive model. Scenario estimated points use adjusted observed zone rates, so the two estimates need not match. Neither measure evaluates whether passing or drawing a foul would have been better.

**Also called / searchable fields:** expected_pps; predicted points / attempt; Predicted pts / attempt; average predicted points per attempt; expected points; what they are worth; shot quality; expected

**Related:** EP / ep: scenario estimated points per attempt; Make probability: chance of a successful shot; PPS: observed points per attempt

### Share of attempts: a zone's part of the mix

A zone's share is the fraction of all selected attempts taken from that zone. The shares across the five zones add to 100%.

**Example:** 30 corner threes out of 200 total attempts gives 30 ÷ 200 = 15% corner-three share. It is not a 15% chance of making a corner three.

**More detail:** A share describes shot selection rather than shooting accuracy. Three-point share combines corner and above-break three zones. Exported share values use decimals: 0.15 means 15%. Changing the team or player changes the denominator and can change every zone's share even when its raw attempt count is similar.

**Also called / searchable fields:** share; share of attempts; shot share; zone share; three_point_share; three-point share

**Related:** Shot mix: how attempts are distributed; FG% / fg_pct: field-goal percentage; Percentage points (pp) versus percent change

### Court map, heatmap, cells and color scale

Each square groups shots from approximately the same three-foot court area. Its color summarizes attempts, average make probability, or average predicted points, depending on the map.

**Example:** A dark square on Attempts means many shots were recorded there. A dark square on Make probability means a higher estimated chance. Read the labeled scale below each map.

**More detail:** These maps measure different quantities, so their colors are not directly interchangeable. Count scales can change between selections. The probability scale runs from 0 to 1; the points map displays a scale from 0 to 2. Hover shows the cell's sample count. Blank cells have no eligible support; they are not zero-probability locations. Court lines provide orientation but do not assign the source's zone labels.

**Also called / searchable fields:** map; heatmap; court explorer; cell; bin; grid; color scale; colour scale; legend; hover; half-court; where shots happen; recorded attempt frequency

**Related:** Minimum attempts per model-map cell; Coordinates, distance, angle and feet; Zones and the zone breakdown

### Minimum attempts per model-map cell

This setting hides cells with too few recorded attempts in the probability and expected-points maps. The Attempts map keeps all visible recorded attempts.

**Example:** With a minimum of 5, a cell containing 4 shots is blank on the two model maps. Raising the setting to 10 also hides cells with 5–9 shots.

**More detail:** A higher minimum trades map coverage for a larger local sample. It does not retrain the model, remove shots from the top summary, or change scenario eligibility. A blank cell means there is no displayed estimate supported by this threshold, not that shots cannot be made there. A threshold is a rule used to decide whether information is shown.

**Also called / searchable fields:** minimum attempts per model-map cell; cell minimum; threshold; blank cell; empty cell; low-count cells; eligible support

**Related:** Court map, heatmap, cells and color scale; Sample support: limited, usable and broader

### Coordinates, distance, angle and feet

Coordinates describe a shot's position on the court. Distance tells how far it is from the basket, measured in feet. Angle describes its direction relative to the basket.

**Example:** A distance of 10 ft is ten feet. A distance band such as 10–15 ft groups attempts in that range; it is not a single exact location.

**More detail:** shot_x is the chart's lateral coordinate and shot_y its up-court coordinate under the native source convention. Coordinates are discretized, meaning positions are limited to recorded steps rather than continuous precise tracking. Some attempts fall outside the drawing and remain in totals. The model uses distance and a symmetric angle from those inputs. Here ft is a distance unit; uppercase FT usually means free throw.

**Also called / searchable fields:** shot_x; shot_y; dist_ft; coordinates; coordinates_or_distance; distance; angle; feet; distance in ft; discretized; displayed half-court; outside this view; distance_band

**Related:** Zones and the zone breakdown; Nonlinear spline and distance bands; Coverage, missing data and limitations

### Zones and the zone breakdown

A zone is a broad area used to group attempts. CourtSense uses five source-defined zones: at the rim, paint, midrange, corner three and above-break three.

**Example:** The zone table lets you compare a zone's attempt count, make rate, points per attempt and share without reading every map cell.

**More detail:** Zones are broader than map cells and are inferred by the upstream source geometry adapter. They are not verified shot-tracking labels or recomputed from the displayed court lines. In particular, Paint is a source distance band, not proof a shot was inside the painted lane. Imperfect coordinates can affect boundaries. A zone with no attempts cannot support an observed rate. CSV files may use codes such as mid or abovebreak3.

**Also called / searchable fields:** zone; zones; shot_zone; court zone; zone breakdown; source-defined zones; source geometry

**Related:** At the rim / rim; Paint / lane; Midrange / mid; Corner three / corner3; Above-break three / abovebreak3

### At the rim / rim

At the rim groups attempts the upstream geometry adapter places within its near-basket distance band. Such shots can include layups and dunks, but play type is not verified here.

**Example:** Ten makes from 15 rim attempts gives 66.7% observed shooting and, if all are twos, 1.33 observed points per attempt.

**More detail:** The rim code names a location group; it does not identify every play as a layup or dunk. A high rim rate does not mean a team can create unlimited rim opportunities. Defender position, passes and available lanes are not fully captured. Use the source label as a broad description rather than a precise claim about shot technique.

**Also called / searchable fields:** rim; at the rim; near the basket; layup; dunk

**Related:** Zones and the zone breakdown; Shot availability and unchanged efficiency

### Paint / lane

Paint usually means the marked lane near the basket. In this dataset, however, the label names a short-distance band of non-rim two-point attempts, not a verified lane boundary.

**Example:** The upstream adapter can label a non-rim two within 15 feet as Paint even if its chart position is outside the drawn lane. Read the table as a source grouping.

**More detail:** The native geometry adapter places non-rim twos within its 15-foot distance cutoff in this category. It does not verify post-ups, floaters or whether a shot was physically inside the painted key. Rim and Paint are mutually exclusive categories, so shots are not counted in both. This distinction matters when explaining why the map's court lines do not perfectly match zone totals.

**Also called / searchable fields:** paint; lane; key; inside the lane

**Related:** Zones and the zone breakdown; At the rim / rim; Defender distance, fatigue, shot clock and play type

### Midrange / mid

Midrange groups geometry-inferred two-point attempts outside the source's rim and short-distance Paint categories.

**Example:** A midrange two made 40% of the time gives about 0.40 × 2 = 0.80 points per attempt before any free-throw effects.

**More detail:** A lower average than a three-point zone does not prove that every midrange attempt is a bad choice. Late-clock situations, defense and alternative actions matter. Those options are not all observed. Treat the comparison as a question for further review, and consider the sample size and source zone quality.

**Also called / searchable fields:** mid; midrange; mid-range; long two

**Related:** Zones and the zone breakdown; Predicted points per attempt / expected_pps; Association versus cause and effect

### Corner three / corner3

Corner three groups source-labeled three-point attempts near the baseline corners of the court.

**Example:** A 36% corner-three make rate gives 0.36 × 3 = 1.08 points per attempt. Its share measures how often those attempts are taken.

**More detail:** The baseline is the court's end boundary behind the basket. A strong corner rate may reflect open attempts, particular shooters or a small sample. The app does not observe every pass or defender reaction needed to create more corner threes. Source coordinates and court rules can affect boundary interpretation.

**Also called / searchable fields:** corner3; corner three; corner three-pointer; baseline; corner threes

**Related:** Above-break three / abovebreak3; Share of attempts: a zone's part of the mix; Shot availability and unchanged efficiency

### Above-break three / abovebreak3

Above-break three groups source-labeled three-point attempts around the rest of the arc, away from the baseline corner-three category.

**Example:** A three from near the top of the arc is generally part of this group; a baseline-corner three belongs to Corner three.

**More detail:** Break refers to the transition between the corner portion and the main curved arc. The term does not mean a fast break. This is a broad location grouping rather than a tracked play type. The project keeps the source's category and point value; the drawing provides orientation rather than reclassifying each shot.

**Also called / searchable fields:** abovebreak3; above-break three; above break three; arc; three-point line

**Related:** Corner three / corner3; Zones and the zone breakdown

## Shot-mix scenarios

### Shot mix: how attempts are distributed

Shot mix describes the percentage of attempts taken from each zone. The recorded mix is what happened; the scenario mix is a proposed distribution under the selected limits.

**Example:** Moving from 20% to 25% corner threes means taking five more corner threes per 100 total attempts and five fewer attempts elsewhere.

**More detail:** All five shares must sum to 100%, so an increase needs a decrease somewhere else. current_share stores recorded shares and recommended_share stores the scenario shares as decimals. The word recommended names the optimizer's output, not proven coaching advice. The scenario assumes efficiencies remain similar after reallocating shots.

**Also called / searchable fields:** shot mix; recorded mix; scenario mix; current_share; recommended_share; recorded shot share; scenario shot share; allocation

**Related:** Percentage points (pp) versus percent change; Scenario, retrospective and conditional estimate; Shot availability and unchanged efficiency

### Scenario, retrospective and conditional estimate

A scenario asks what the estimated scoring average could be under a different shot mix. Retrospective means it uses past recorded attempts.

**Example:** If the adjusted current mix estimates 1.00 points per attempt and the scenario estimates 1.03, the conditional difference is +3 points per 100 attempts.

**More detail:** Conditional means the answer depends on assumptions, especially that each zone's estimated efficiency persists after the mix changes. current_ep and recommended_ep are the weighted averages under the two mixes. The main scenario uses the sidebar selection; comparison report cards use fixed default limits. An intervention result would require observing a real strategy change, which has not been conducted here.

**Also called / searchable fields:** scenario; shot-mix scenarios; retrospective; conditional; recommendation; intervention result; current_ep; recommended_ep; current mix · estimated pts / attempt; scenario mix · estimated pts / attempt

**Related:** EP / ep: scenario estimated points per attempt; Estimated change or gain per 100 attempts; Association versus cause and effect; Prospective validation, protocol and analyzer

### Percentage points (pp) versus percent change

Percentage points measure the direct difference between two percentages. Percent change measures that difference relative to the starting value.

**Example:** Moving from 20% to 25% is +5 percentage points, but a 25% relative increase: (25 − 20) ÷ 20 × 100. The scenario sliders use percentage points.

**More detail:** Percent means per hundred. A decimal such as 0.25 becomes 25% when multiplied by 100. A share difference of 0.05 means five percentage points. Keep these units separate when describing a scenario: five extra attempts per 100 total attempts is a five-point share shift, not a five-percent relative increase from every starting share.

**Also called / searchable fields:** pp; percentage points; percentage-point; percent change; %; decimal; percent; percentage

**Related:** Share of attempts: a zone's part of the mix; Total mix movement / L1 budget; Maximum shift per zone

### Maximum shift per zone

This control limits how many percentage points each individual zone's share may rise or fall from its recorded share.

**Example:** With a 5 pp limit, a zone starting at 20% can range from 15% to 25%, subject to the other constraints.

**More detail:** A zone cannot fall below 0% or exceed 100%. The movement budget and three-point cap can restrict its change further. A zero shift holds all shares fixed; that can be infeasible if the recorded mix already violates another limit. In exports max_shift is a decimal such as 0.05 for five percentage points.

**Also called / searchable fields:** maximum shift per zone; max_shift; zone limit; stricter limits; ±5

**Related:** Total mix movement / L1 budget; Three-point share cap; Feasible, infeasible and constraints

### Total mix movement / L1 budget

Total mix movement adds the size of every increase and every decrease in zone share. It counts both sides of a transfer.

**Example:** Moving five percentage points from midrange to corner threes uses ten points of movement: 5 down + 5 up. A 20-point budget allows at most 10% of all attempts to be reassigned.

**More detail:** Mathematically this is an L1 distance: the sum of absolute differences between scenario and recorded shares. Absolute means ignore the plus or minus sign. budget = 0.20 means twenty percentage points of total movement. Individual zone limits, unsupported zones and the three-point cap may allow less movement than the budget.

**Also called / searchable fields:** total mix movement; movement budget; budget; L1; absolute changes; total movement

**Related:** Percentage points (pp) versus percent change; Maximum shift per zone; Enough evidence to change mix / eligible

### Three-point share cap

The cap limits the combined share of corner-three and above-break-three attempts in the scenario.

**Example:** A 60% cap permits no more than 60 threes per 100 total field-goal attempts. It does not mean the team is expected to make 60% of its threes.

**More detail:** The cap is a modeling choice, not an NCAA rule. If the recorded three-point share is above the cap and the allowed movement is too small to reduce it enough, no feasible scenario exists. A decimal three_cap = 0.60 means a 60% share cap. Raising it does not guarantee a gain or create real shooting opportunities.

**Also called / searchable fields:** three-point share cap; three_cap; three point cap; cap; maximum threes

**Related:** Feasible, infeasible and constraints; Share of attempts: a zone's part of the mix; Shot availability and unchanged efficiency

### Uncertainty penalty / risk

This control reduces the appeal of zones whose estimated points are more variable. Higher settings favor estimates with less resampling variation.

**Example:** Two zones can have similar average expected points. If one has a much more variable estimate, a larger penalty can make the optimizer favor the other.

**More detail:** The optimizer subtracts the selected penalty times a zone's bootstrap standard deviation from its estimated points when choosing shares. The displayed scoring gain still uses the unpenalized point estimates. risk = 1.0 is a multiplier, not 100% risk or a confidence level. It cannot account for every real-world uncertainty, including changes in defense and shot availability.

**Also called / searchable fields:** uncertainty penalty; risk; risk penalty; risk adjustment; sensitivity control

**Related:** Standard deviation (SD); Bootstrap, game resampling and clusters; Sensitivity and season stability

### Adjusted make rate, shrinkage and shrunk_fg

An adjusted make rate blends a zone's observed shooting with an earlier pooled reference rate. This makes estimates from a few shots less extreme.

**Example:** With 4 makes in 5 attempts and a 40% reference worth 30 prior attempts, the adjusted rate is (4 + 30 × 0.40) ÷ (5 + 30) = 45.7%, instead of the raw 80%.

**More detail:** The scenario uses 30 prior attempts of weight. A large real sample receives much less adjustment than a small one. The prior comes from earlier pooled zone evidence where available. Shrinkage is an estimation method, not a change to the recorded makes. shrunk_fg belongs to the scenario; the frozen shot model uses a separate set of inputs and training procedure.

**Also called / searchable fields:** adjusted make rate; shrinkage; shrunk_fg; shrunk; stabilize; smoothed rate; small sample adjustment

**Related:** Prior and pooled reference rate; Raw or unadjusted rate; EP / ep: scenario estimated points per attempt

### Raw or unadjusted rate

A raw rate is calculated directly from the selected observed records, without blending in a reference rate or correcting for opponents.

**Example:** Making 4 of 5 shots gives a raw 80% make rate. The small denominator makes it much less stable than 800 of 1,000.

**More detail:** Raw does not mean wrong; it means the calculation has not received that particular adjustment. raw_fg is an exported raw make rate. Raw source files are a different use of the word: they are the original downloaded records before cleaning. Read whether raw describes a statistical rate or a file.

**Also called / searchable fields:** raw; unadjusted; raw rate; raw make rate; unadjusted rate

**Related:** FG% / fg_pct: field-goal percentage; Adjusted make rate, shrinkage and shrunk_fg; Data audit, cleaning and duplicate checks

### Prior and pooled reference rate

A prior is reference information blended with the current sample. Pooled means it combines observations from a broader group rather than one selected player.

**Example:** A 40% prior with a weight of 30 acts like 12 reference makes in 30 reference attempts for the shrinkage calculation.

**More detail:** Those are mathematical weights, not 30 additional shots actually taken by the player. The scenario's pooled zone prior and the model's player-history prior are separate. The model starts with weak fixed zone reference rates and updates history only from earlier dates within that season. zone_prior stores pooled scenario rates; prior_attempts settings specify their strength. More weight creates more shrinkage toward the reference.

**Also called / searchable fields:** prior; pooled prior; pooled rate; zone_prior; zone_prior_attempts; history_prior_attempts; reference rate; prior attempts

**Related:** Adjusted make rate, shrinkage and shrunk_fg; Earlier player history and history size

### EP / ep: scenario estimated points per attempt

In the scenario table, EP is the adjusted make rate multiplied by the zone's two- or three-point value.

**Example:** An adjusted three-point make rate of 35% gives EP = 0.35 × 3 = 1.05. The current and scenario mixes average these values using their respective shares.

**More detail:** EP describes the selected sample after shrinkage. The court's predicted points instead average the frozen model's shot-level probabilities, so the numbers can differ. ep_low and ep_high are resampling bounds for a zone's adjusted points. An EP estimate does not include free throws or possessions that end in a turnover.

**Also called / searchable fields:** EP; ep; estimated points / attempt; estimated points per attempt; zone efficiency

**Related:** Adjusted make rate, shrinkage and shrunk_fg; Predicted points per attempt / expected_pps; Lower and upper bounds / low and high

### Estimated change or gain per 100 attempts

This expresses the difference between the scenario and current estimated points per attempt over a fixed 100 field-goal attempts.

**Example:** A rise from 1.02 to 1.05 gives (1.05 − 1.02) × 100 = +3 estimated points per 100 attempts.

**More detail:** A positive value indicates a conditional estimated increase; a negative value indicates a decrease. It is not a forecast of the next game's score, because games contain different attempt counts and other offensive events. Read its 95% interval and the unchanged-efficiency assumption before describing it as an opportunity. A zero result can reflect unchanged shares or no supported improvement under the limits.

**Also called / searchable fields:** estimated change / 100 attempts; gain_per100; estimated gain / 100; conditional gain / 100; gain; estimated opportunity

**Related:** 95% interval / CI and uncertainty; Scenario, retrospective and conditional estimate; Association versus cause and effect

### Enough evidence to change mix / eligible

A zone is eligible to have its share changed only when the selected data contains at least 30 attempts in that zone across at least five games.

**Example:** A zone with 35 attempts in six games can qualify. A zone with 35 attempts in two games does not, because it lacks enough game-level support.

**More detail:** Unsupported zones are held at their recorded share by the optimizer. This prevents it from reallocating attempts based on very limited evidence. The page requires at least 100 total attempts to offer the main scenario, and the engine also needs at least five games. These safeguards are separate from the map-cell minimum and do not prove that a strategy will succeed.

**Also called / searchable fields:** eligible; enough evidence to change mix; unsupported zones; insufficient evidence

**Related:** Sample support: limited, usable and broader; Minimum attempts per model-map cell; Feasible, infeasible and constraints

### Feasible, infeasible and constraints

Feasible means at least one shot mix satisfies all selected rules. Infeasible means those rules cannot all be satisfied together.

**Example:** If a team takes 70% threes, a 60% cap requires a ten-point reduction. A movement budget of only ten points cannot transfer that much because it counts both decreases and increases.

**More detail:** The optimizer searches for the strongest penalized estimate within the zone limits, movement budget, cap and evidence rules. A feasible result is mathematically allowed, not necessarily possible on court. Infeasible results have no valid gain to interpret. Try allowing more movement or raising the cap, then check the assumptions. Status in a hypothesis table instead describes a research claim's outcome; it is not scenario feasibility.

**Also called / searchable fields:** feasible; infeasible; constraints; limits; message; status; optimization; optimizer; linear program

**Related:** Total mix movement / L1 budget; Three-point share cap; Shot availability and unchanged efficiency

### Shot availability and unchanged efficiency

The scenario assumes a different mix can be taken while each zone remains similarly efficient. The records do not tell us whether all those extra opportunities would actually exist.

**Example:** Taking more corner threes might mean using less-open shots or different shooters. The past corner-three rate may then stop being a good estimate.

**More detail:** Defense, fatigue, play calls, roster changes and available passes can alter both opportunity and success. The model does not fully measure these factors. A scenario is useful for generating a question to examine in video or a future study; it is not a playbook instruction or proof that more of a high-value zone will always help.

**Also called / searchable fields:** shot availability; new shot opportunities; efficiency persists; unchanged efficiency; available passing options; roster changes; defenders

**Related:** Association versus cause and effect; Defender distance, fatigue, shot clock and play type; Prospective validation, protocol and analyzer

## Evidence & uncertainty

### Sample support: limited, usable and broader

Sample support describes how many attempts and distinct games contribute to an estimate. More observations usually make an average less sensitive to a few unusual results.

**Example:** Usable support means at least 30 attempts in five games. Broader support means at least 100 attempts in ten games. Smaller samples are labeled Limited sample.

**More detail:** These are descriptive project thresholds, not probabilities that a recommendation is correct. A large sample can still be biased, poorly measured or unrepresentative of future games. Attempts in one game share conditions, so game count matters alongside shot count. The top small-sample warning uses fewer than 100 total attempts; zone labels use zone-specific counts.

**Also called / searchable fields:** sample support; support; limited sample; usable support; broader support; usable; broader; small sample; sample size; how much evidence

**Related:** Games represented and distinct games; Bootstrap, game resampling and clusters; Coverage, missing data and limitations

### Games represented and distinct games

Games represented counts different game identifiers among the selected shot records. A game with many attempts still counts once for that selection.

**Example:** If a player's 60 available attempts span four games, Games represented is 4, not 60. Two players in the same game do not create two distinct games in a combined shot selection.

**More detail:** This is a count of covered games, not a guarantee of a complete schedule. Team-games on Team context is a different unit: each team's participation counts separately. Game-level resampling keeps attempts from the same game together because they can share opponents, conditions and lineup effects.

**Also called / searchable fields:** games; games represented; distinct games; game count; contest count

**Related:** Team-games versus games; Coverage, missing data and limitations; Bootstrap, game resampling and clusters

### 95% interval / CI and uncertainty

An interval shows a range of estimates from resampling the available data. A wider interval indicates more variability under that calculation.

**Example:** A gain interval from −1 to +4 points per 100 attempts includes both losses and gains. These data do not clearly separate that fixed scenario from no change.

**More detail:** CourtSense uses the 2.5th and 97.5th percentiles of bootstrap estimates as a 95% interval. For scenario gain, the selected shot mix stays fixed during resampling. The range describes sampling variation under the model assumptions. It is not a 95% guarantee of a future score, and it does not cover every error from defense changes, missing data or choosing a strategy after seeing results. Excluding zero still does not establish cause and effect.

**Also called / searchable fields:** 95% interval; CI; confidence interval; conditional 95% interval; uncertainty; resampling bounds; crosses zero; includes zero; excludes zero; test_confidence_intervals

**Related:** Bootstrap, game resampling and clusters; Lower and upper bounds / low and high; Association versus cause and effect

### Lower and upper bounds / low and high

A lower bound is the bottom of a reported interval; an upper bound is its top. Read the quantity and units beside the bounds.

**Example:** ep_low = 0.90 and ep_high = 1.10 describe a zone's points per attempt. gain_low = −1 and gain_high = +4 describe a scenario change per 100 attempts.

**More detail:** Bounds from different measures cannot be compared as if they had the same units. low and high in test_confidence_intervals belong to validation scores or their differences. The gain interval resamples the scoring difference directly; subtracting two separately reported EP bounds is not the same calculation.

**Also called / searchable fields:** low; high; lower 95% bound; upper 95% bound; ep_low; ep_high; gain_low; gain_high; lower bound; upper bound

**Related:** 95% interval / CI and uncertainty; Estimated change or gain per 100 attempts; EP / ep: scenario estimated points per attempt

### Bootstrap, game resampling and clusters

Bootstrap resampling creates many alternative datasets by sampling recorded groups again, with replacement, and recalculating the estimate.

**Example:** When sampling ten games, one game may be chosen twice and another not at all. All shots from each chosen game stay together. The estimate is recalculated for each sample.

**More detail:** With replacement means a group can be selected more than once. Game clusters preserve shared conditions within a game. The main analysis uses 500 resamples; some display intervals use their own repeat setting. The prospective analyzer groups by sessions. Percentiles mark positions in the sorted estimates. Resampling quantifies variation within the available evidence; it cannot create information about unobserved opponents or strategy reactions.

**Also called / searchable fields:** bootstrap; resampling; game-resampling; game resampling; cluster; session-cluster; bootstrap_repeats; repeats; percentile

**Related:** 95% interval / CI and uncertainty; Random seed and repeatability; Games represented and distinct games

### Standard deviation (SD)

Standard deviation measures how spread out values are around their average. A larger value means greater variation.

**Example:** If one zone's resampled points estimates stay near 1.00 while another's range widely, the second has the larger bootstrap standard deviation.

**More detail:** Standard deviation is expressed in the units of the measured quantity. It is not the same as a 95% interval or a shooting percentage. The scenario's uncertainty penalty uses each zone's bootstrap standard deviation to prefer more stable estimates when other factors are similar. A small value does not rule out bias or missing information.

**Also called / searchable fields:** SD; std; standard deviation; variation; variability

**Related:** Uncertainty penalty / risk; 95% interval / CI and uncertainty

### Sensitivity and season stability

A sensitivity check asks whether the conclusion changes when an assumption or limit changes. Season stability compares separately calculated historical scenarios across seasons.

**Example:** The diagnostic tries zone limits of 2.5, 5 and 10 percentage points while keeping its other default controls fixed. A zone that only looks attractive under one setting deserves closer review.

**More detail:** The diagnostic uses default movement, cap and uncertainty settings, so it may differ from the main customized scenario. Cross-season stability can change with rosters, schedules and coverage. It is not a fresh model evaluation or evidence that a player retained the same source identity. An unavailable season means it lacked enough support for a feasible comparison.

**Also called / searchable fields:** sensitivity; sensitivity check; season stability; historical scenario stability; check stricter limits and season stability; zones with increased share

**Related:** Maximum shift per zone; Season and ending-year codes; Model validation and evaluation season

### Association versus cause and effect

An association means two patterns appear together in the data. A causal claim says changing one thing would itself change the outcome.

**Example:** Players may make more shots near the rim, but that alone does not prove telling a team to take more rim shots will improve its score. The available shots and defense can also change.

**More detail:** CourtSense reports descriptive comparisons and conditional scenarios. It does not adjust team comparisons for every opponent or schedule difference. Even a positive gain interval or a model coefficient is not proof of cause. A carefully designed future experiment could test a strategy; no real prospective experiment has been conducted for this project.

**Also called / searchable fields:** causal; causality; association; correlation; descriptive; not opponent-adjusted; schedule adjustment; cause and effect; intervention

**Related:** Shot availability and unchanged efficiency; Prospective validation, protocol and analyzer; Coefficient: a model association

## Compare teams & player development

### Compare teams and printable report cards

Compare teams puts two whole-team selections beside each other using the same season. Report cards summarize a team's evidence in a downloadable handout.

**Example:** Compare their observed points per attempt, predicted values and zone support. A higher rate can prompt a question about shot selection, but it is not an opponent-adjusted team ranking.

**More detail:** The page has its own First team and Second team controls; sidebar player filters do not restrict it. Each default scenario uses ±5 pp per zone, a 20 pp movement budget, a 60% three-point cap and penalty 1.0. Training-season predictions are in-sample. Download a team's HTML report, open it in a browser and use Print → Save as PDF. A strongest zone means the highest observed rate among zones with usable support.

**Also called / searchable fields:** compare teams; team report card; report card; strongest observed zone; estimated opportunity; printable team report; comparison

**Related:** Selection, scope and filters; Sample support: limited, usable and broader; In-sample predictions; HTML and browser report cards

### Player development and video-review prompts

Player development shows one selected profile's season, zone evidence and scoring trends. Its practice prompts suggest questions for video review.

**Example:** If a player's paint attempts score below the model's estimate, review those attempts for balance, preparation and defensive pressure before deciding whether a drill is useful.

**More detail:** An observed-minus-predicted gap is not a diagnosis of poor skill. Shot difficulty, luck, source errors and missing context can explain it. The Player profile control can differ from the sidebar's Player control. Source IDs are treated within one season, and similar names are not automatically merged. The app offers evidence for review rather than validated coaching prescriptions.

**Also called / searchable fields:** player development; practice priority; practice / video-review prompt; video-review priority; observed strength; drill; training prescription

**Related:** Observed-minus-predicted gap; Game trend and recent five-game average; ID, player keys and game identifiers

### Game trend and recent five-game average

A game trend shows the observed and predicted points per attempt for each game. Recent 5 games smooths the observed rate using up to five consecutive recorded games.

**Example:** If those games contain 50 total points and 40 total attempts, the recent rate is 50 ÷ 40 = 1.25. A game with one shot does not receive the same weight as a game with twenty.

**More detail:** The calculation uses a ratio of totals, rather than averaging each game's percentage equally. Early windows contain fewer than five games. points in the player CSV is field-goal points; points in Team context is the team's complete score including free throws. A trend can reflect opponents and changing attempts as well as ability. Missing source games mean five recorded games may not be five games on the actual schedule.

**Also called / searchable fields:** trend; game trend; recent 5 games · observed; recent five-game average; rolling average; rolling window; game-by-game; points

**Related:** PPS: observed points per attempt; Coverage, missing data and limitations; Mean, average, ratio of totals and weights

### Observed-minus-predicted gap

The gap subtracts predicted points per attempt from the observed rate for the same recorded shots.

**Example:** Observed 1.10 minus predicted 1.00 gives +0.10. Observed 0.90 minus predicted 1.00 gives −0.10. The sign says which average was larger.

**More detail:** A negative gap can guide video review but does not prove a skill deficit. Small samples, difficult shots not captured by the model and chance can all affect it. Training-season gaps use in-sample predictions and deserve extra care. A validation-score difference instead compares error scores; lower scores are better, so its sign needs a separate reading.

**Also called / searchable fields:** gap; observed-minus-predicted; observed minus predicted; difference; outperform; underperform

**Related:** Player development and video-review prompts; In-sample predictions; Model validation and evaluation season

### Mean, average, ratio of totals and weights

A mean adds values and divides by how many values there are. A ratio of totals adds all points or makes first, then divides by all attempts or possessions.

**Example:** One game has 1 make in 1 attempt; another has 0 in 9. Overall FG% is 1 ÷ 10 = 10%, rather than the equally weighted game-rate average of 50%.

**More detail:** A denominator is the number underneath a fraction, such as attempts in makes ÷ attempts. The numerator is the number above it. Ratios of totals effectively give more weight to games with more attempts. Mean Brier score and mean log loss average one error value per evaluated shot. Always check which observations are being averaged and whether the units match.

**Also called / searchable fields:** mean; average; weighted average; ratio of totals; ratios of totals; denominator; numerator

**Related:** FG% / fg_pct: field-goal percentage; Game trend and recent five-game average; Mean Brier score: squared probability error; Mean log loss: penalty for the actual result

## Team context

### Team context: the whole offense

Team context adds free throws, turnovers and offensive rebounds using checked team box scores. It describes whole teams rather than a selected player's shots.

**Example:** The top shot cards may exclude free throws, while Team context includes them in total team points. The two pages therefore measure different parts of offense.

**More detail:** A box score is a game's statistical summary. Reconciled means the project checks box-score field-goal counts and total points against its shot data before including the paired teams. Context may cover fewer games because these checks can reject unmatched games. Possessions are estimated from totals, not reconstructed from individual plays. The source's home/away labels are descriptive and can include neutral-site games.

**Also called / searchable fields:** team context; whole offense; box score; reconciled box scores; team score; team_score; total points

**Related:** Estimated possessions; Reconciliation and joining shot data to box scores; Source designation: home, away and neutral site

### Estimated possessions

A possession is an offensive opportunity. The app estimates how many there were from box-score totals because complete possession sequences have not been reconstructed.

**Example:** For one team: 60 FGA − 10 offensive rebounds + 12 turnovers + 0.475 × 20 FTA = 71.5 estimated possessions. The app averages the two teams' estimates for that game.

**More detail:** Subtracting offensive rebounds avoids treating every rebound-and-shot as a brand-new possession. The free-throw coefficient accounts approximately for trips to the line; not every free throw ends a possession. Fractional results are normal in an estimate. The formula uses total turnovers. It does not directly identify exact second-chance sequences or use the shot count alone as the number of possessions.

**Also called / searchable fields:** possession; possessions; estimated_possessions; raw_possessions; possession estimate; FGA − OR + TO; 0.475; second-chance

**Related:** Points per estimated possession / PPP; OR / ORB: offensive rebounds; TO / TOV: turnovers; FTA: free-throw attempts

### Points per estimated possession / PPP

This divides total team points, including free throws, by estimated possessions. It describes scoring across the whole offense.

**Example:** Scoring 75 points over 70 estimated possessions gives 75 ÷ 70 = 1.071 points per estimated possession, or about 107.1 per 100 estimated possessions.

**More detail:** CourtSense displays the per-possession rate, not a per-100 offensive rating. It uses ratios of totals across included team-games and makes no opponent or schedule adjustment. The possession count is approximate. Do not compare it directly with field-goal points per attempt: a possession can involve free throws, turnovers and offensive rebounds in addition to an attempted field goal.

**Also called / searchable fields:** PPP; points / estimated possession; points per possession; offensive efficiency; offensive rating

**Related:** Estimated possessions; PPS: observed points per attempt; Association versus cause and effect

### FT / FTM: free throws made and free-throw points

A free throw is a shot awarded under the rules, generally after a foul. Each made free throw scores one point. FTM means free throws made.

**Example:** Making 14 free throws contributes 14 free-throw points. These points appear in Team context but not in the field-goal shot model.

**More detail:** The context field free_throws counts makes, not attempts. A trip to the line may involve more than one free throw, so free-throw counts are not possession counts. Uppercase FT usually means free throw in basketball; ft after a distance means feet. The app uses source box-score totals rather than attaching foul sequences to every mapped field-goal attempt.

**Also called / searchable fields:** FT; FTM; free_throws; free throws; free throws made; free-throw points; foul shot

**Related:** FTA: free-throw attempts; Point value: two or three points; Estimated possessions

### FTA: free-throw attempts

FTA counts all free throws tried, including misses. It differs from FTM, which counts only successful free throws.

**Example:** Making 14 of 20 free throws means FTM = 14, FTA = 20 and free-throw percentage = 70%.

**More detail:** Estimated possessions use 0.475 times FTA as an approximate contribution from free-throw opportunities. FTA is not added to field-goal attempts in the court maps. A missed free throw contributes no point, but remains an attempt. The app does not reconstruct every free-throw trip or foul-and-rebound sequence.

**Also called / searchable fields:** FTA; free_throw_attempts; free_throws_attempted; free-throw attempts

**Related:** FT / FTM: free throws made and free-throw points; Estimated possessions

### TO / TOV: turnovers

A turnover is a loss of possession to the opponent without completing the intended scoring opportunity. TO and TOV are common abbreviations.

**Example:** Ten turnovers over 70 estimated possessions gives 10 ÷ 70 × 100 = 14.3 turnovers per 100 estimated possessions.

**More detail:** Team context uses total turnovers, including the source's team totals, in its possession estimate. A turnover often produces no field-goal attempt, which is why shot-only PPS cannot measure the full cost. The displayed rate adjusts for the estimated number of offensive opportunities; it does not adjust for the opponent's defense.

**Also called / searchable fields:** TO; TOV; turnover; turnovers; total_turnovers; turnovers / 100 estimated possessions

**Related:** Estimated possessions; Points per estimated possession / PPP

### OR / ORB: offensive rebounds

An offensive rebound is recovering the ball after your own team's missed shot. It can create another shot within the same offensive opportunity.

**Example:** A team can miss, regain the ball and shoot again. Counting both shots as separate possessions would overcount that sequence; the possession formula subtracts offensive rebounds.

**More detail:** The app has aggregate offensive-rebound totals, not a complete chain linking each rebound to a specific second-chance shot. It therefore does not claim exact second-chance efficiency. A high rebound count alone also depends on how many misses were available to rebound.

**Also called / searchable fields:** OR; ORB; offensive rebounds; offensive_rebounds; offensive rebound; rebound

**Related:** Estimated possessions; Defender distance, fatigue, shot clock and play type

### Team-games versus games

A team-game is one team's participation in one game. A game involving two included teams contributes two team-games to an all-team context total.

**Example:** A game between Ohio State and another included Division I team counts as one distinct game in combined shot data but two team-games in Team context.

**More detail:** For a single team's context, ten games generally mean ten team-games. For all teams, summing participation counts is not the number of unique games. Context rates divide aggregated points by aggregated estimated possessions, so counting both teams is deliberate. Check the unit before comparing a context total with Games represented on the shot cards.

**Also called / searchable fields:** team-games; team games; team_rows; designation games

**Related:** Games represented and distinct games; Team context: the whole offense

### Source designation: home, away and neutral site

Home and away are labels supplied by the box-score source. A designated home team may still be playing at a neutral tournament site.

**Example:** A tournament game can list one team as home for administrative purposes. Its statistics should not automatically be interpreted as performance in that team's own arena.

**More detail:** Team context groups included team-games by source designation. Differences between groups can reflect opponents, sample sizes, schedules and venues. They do not establish a home-court effect. The app does not treat source designation as verified venue information or add game-final scores as predictors of earlier shots.

**Also called / searchable fields:** designation; source designation; home; away; neutral site; home-court effect; home away splits

**Related:** Association versus cause and effect; Team context: the whole offense

## Model validation

### Model validation and evaluation season

Validation compares the probabilities with the makes and misses that actually happened on evaluation shots. It checks the model before treating its estimates as useful evidence.

**Example:** Compare models using the same season and attempts. Lower mean Brier score and lower mean log loss indicate better probability estimates on those shots.

**More detail:** The Evaluation season selector is independent of the sidebar team and player. Results cover the full eligible evaluation dataset, not one selected team. The project trains on 2022–23 and 2023–24, selects among candidates using 2024–25 log loss, and performs fixed final evaluation on 2025–26. The displayed scores are not shooting percentages or classification accuracy.

**Also called / searchable fields:** model validation; validation; evaluation season; evaluate; accuracy; accurate; model accuracy; how accurate; how accurate is this model; can I trust the model; model_comparison; selected_model; selection_metric

**Related:** Mean Brier score: squared probability error; Mean log loss: penalty for the actual result; Probability calibration and the diagonal; Training, model selection, held-out and final test

### Mean Brier score: squared probability error

Mean Brier score averages the squared gap between a predicted make probability and the actual result, coded 1 for made and 0 for missed. Lower is better; zero is perfect.

**Example:** For a 70% prediction: a make contributes (0.70 − 1)² = 0.09, while a miss contributes (0.70 − 0)² = 0.49. Average this contribution over all evaluated attempts.

**More detail:** For binary shots, Brier scores range from 0 to 1. It evaluates probabilities, so a model can be useful even when the next outcome remains uncertain. A value of 0.23 is not 23% shooting or 77% accuracy. Compare scores on the same shots and season. Its numerical scale differs from log loss; do not decide which metric is better by comparing their sizes.

**Also called / searchable fields:** Brier; brier score; mean Brier score; brier; squared error

**Related:** Mean log loss: penalty for the actual result; Make probability: chance of a successful shot; Baseline, global rate and zone shrinkage

### Mean log loss: penalty for the actual result

Mean log loss averages how heavily the model is penalized for the probability it assigned to the result that happened. Confident wrong predictions receive especially large penalties. Lower is better; zero is perfect.

**Example:** A 70% make prediction that is made contributes −ln(0.70) ≈ 0.357. If it misses, the predicted miss chance is 30%, so the contribution is −ln(0.30) ≈ 1.204.

**More detail:** ln is the natural logarithm. Per shot, the formula is −[y ln(p) + (1 − y) ln(1 − p)], with p the predicted make chance and y the 0/1 result. The implementation clips extreme probabilities to avoid taking the logarithm of zero. Log loss has no fixed upper limit before clipping. A value near 0.65 is not a 65% miss rate. Compare models on identical evaluated shots.

**Also called / searchable fields:** log loss; log_loss; mean log loss; logarithm; probability penalty; confident wrong predictions

**Related:** Mean Brier score: squared probability error; Make probability: chance of a successful shot; Baseline, global rate and zone shrinkage

### Probability calibration and the diagonal

Calibration asks whether predicted probabilities match observed make rates across many shots. The diagonal represents agreement between the two.

**Example:** If a group averaging 40% predicted chance makes about 40% of its attempts, that group is well calibrated. If it makes only 30%, the prediction was too optimistic.

**More detail:** The chart groups shots into probability bins. Horizontal position is mean prediction; vertical position is observed make rate; n counts the group's shots. Below the diagonal means too optimistic; above means too pessimistic. These bins differ from court-location cells. Agreement in groups does not prove accuracy for every player. Post-hoc calibration means adjusting probabilities after fitting a model; this project evaluates calibration without applying a separate post-hoc transform.

**Also called / searchable fields:** calibration; probability calibration; perfect calibration; post-hoc calibration; calibration transform; diagonal; mean_predicted; observed; calibration bin

**Related:** Make probability: chance of a successful shot; Model validation and evaluation season; Court map, heatmap, cells and color scale

### Baseline, global rate and zone shrinkage

A baseline is a simple reference model. A more complex model should demonstrate better performance against it on the same evaluation shots.

**Example:** Global rate gives every shot the training dataset's overall make rate. Zone shrinkage uses separate stabilized rates for broad court zones.

**More detail:** These baselines help show whether location and player-history inputs add useful predictive information. A small improvement may still matter over many shots, but it should be assessed alongside uncertainty and model complexity. The app selects candidates using 2024–25 mean log loss before the fixed 2025–26 evaluation. A baseline score is model error, not an average team's FG%.

**Also called / searchable fields:** baseline; global rate; global-rate baseline; zone shrinkage; candidates; reference model

**Related:** Model validation and evaluation season; Spatial logistic model; Adjusted make rate, shrinkage and shrunk_fg

### Spatial logistic model

Spatial means related to location. A logistic model combines inputs to estimate a probability between zero and one rather than a raw point total.

**Example:** Two shots can receive different make probabilities because they have different zones, distances, angles or prior shooting histories.

**More detail:** The selected model adds earlier player history to spatial inputs. It is a statistical model, not an AI chatbot. The prediction target is whether a recorded field goal is made. The scenario target instead estimates points under altered zone shares. Logistic regression uses a log-odds calculation internally, and distance is modeled through a spline so its effect need not be a straight line.

**Also called / searchable fields:** spatial; spatial logistic; spatial + player history; logistic regression; estimator; model; prediction_target; scenario_target

**Related:** Feature and standardized input; Nonlinear spline and distance bands; Earlier player history and history size; Odds multiplier and log odds

### Training, model selection, held-out and final test

Training fits the model using earlier data. Selection chooses among candidate models on separate later data. A held-out final test checks the chosen model on data not used to choose it.

**Example:** CourtSense trains on seasons ending 2023 and 2024, selects on 2025, and evaluates the fixed choice on 2026. Those correspond to 2022–23 through 2025–26.

**More detail:** The frozen model is not refitted with the selection season before the final test in this protocol. Earlier dated attempts may update player-history inputs within a season, but the attempt being predicted and future outcomes are excluded. A frozen snapshot is a saved analysis; it is not a continuously updated feed. Repeatedly tuning against the final test would weaken its independence.

**Also called / searchable fields:** training; training_seasons; selection; selection_season; final_test; final_test_season; held-out; held out; test season; freeze; post-freeze

**Related:** Earlier player history and history size; Data leakage and future information; In-sample predictions; Saved snapshot, freeze, run and version

### In-sample predictions

An in-sample prediction describes data used to fit the model. Its apparent agreement can look better than performance on new data.

**Example:** The court can display 2022–23 shots, but their model estimates are training-season descriptions. The later validation seasons provide a stronger check of generalization.

**More detail:** Generalization means working beyond the examples used to learn the model. In-sample maps and player gaps remain useful descriptions if clearly labeled, but they should not be presented as independent evidence of predictive accuracy. The separate Model validation page reports the intended evaluation design.

**Also called / searchable fields:** in-sample; in sample; training-season predicted values; training-season predictions

**Related:** Training, model selection, held-out and final test; Model validation and evaluation season; Observed-minus-predicted gap

### Earlier player history and history size

Player-history inputs summarize shooting information available before a shot's date. They help the model distinguish prior evidence from the current outcome.

**Example:** A shot on January 10 can use the player's earlier dated attempts, but not January 10 outcomes or future games. A new season starts a separate history.

**More detail:** Small histories blend with a weak zone reference using 30 prior attempts. history_logit converts the adjusted chance to log odds; history_size uses log(1 + prior attempts). Online chronological evaluation means earlier test-date outcomes may update this history as dates advance, while fitted model weights stay frozen. Current-day and future outcomes stay excluded. Source IDs are not automatically linked across seasons. This is a history feature, not a complete measure of ability.

**Also called / searchable fields:** player history; prior player results; history_size; history_logit; earlier results; chronological; online chronological evaluation; online evaluation; previous attempts

**Related:** Prior and pooled reference rate; Data leakage and future information; ID, player keys and game identifiers

### Data leakage and future information

Data leakage happens when information that would be unavailable at prediction time sneaks into the model inputs or evaluation process.

**Example:** Using the current shot's made value to predict that same shot, or using a game's final score to predict an earlier attempt, would leak the answer.

**More detail:** The history calculation uses only dates before the predicted shot's date, and the season split keeps fitting, selection and final evaluation separate. Outcomes are legitimate for evaluating the result after prediction, not as inputs that pretend to know the future. Leakage can make a model appear accurate while failing in real use.

**Also called / searchable fields:** leakage; future information; current and future outcomes; game-final scores; outcome as predictor

**Related:** Earlier player history and history size; Training, model selection, held-out and final test; Reproducibility and quality checks

### Feature and standardized input

A feature is information supplied to the model. Standardization rescales some numerical inputs so their changes can be handled consistently during fitting.

**Example:** Distance and angle are numerical features; zone is a category. One-hot encoding represents categories using separate indicator columns.

**More detail:** A standardized coefficient describes a change on the transformed input's scale, not automatically one foot or one percentage point on the original scale. The model includes location features and earlier shooting history, but not every factor affecting a shot. Holding other inputs fixed is a model interpretation, not a controlled real-world experiment.

**Also called / searchable fields:** feature; features; input; predictor; standardized; standardized terms; one-hot; transformed inputs

**Related:** Coefficient: a model association; Nonlinear spline and distance bands; Defender distance, fatigue, shot clock and play type

### Nonlinear spline and distance bands

A spline lets the model represent a smoothly changing effect of distance without forcing one straight-line relationship.

**Example:** The estimated difference between a 5-foot and 10-foot shot need not equal the difference between a 20-foot and 25-foot shot.

**More detail:** Knots are points used to build the spline's pieces. The project uses five knots and a cubic distance spline. Because distance uses multiple transformed inputs, one coefficient alone does not describe its full effect. The report compares held-out distance bands instead. observed_fg and predicted_fg in that profile are observed and mean predicted make rates within each band.

**Also called / searchable fields:** spline; nonlinear; nonlinear spline; distance bands; distance_profile; knots

**Related:** Coordinates, distance, angle and feet; Coefficient: a model association; Prespecified hypotheses / H1–H4

### Coefficient: a model association

A coefficient describes how one transformed model input is associated with prediction log odds while other model inputs are held fixed.

**Example:** A positive coefficient increases modeled make odds as that input rises; a negative coefficient decreases them. It does not directly add that number to shooting percentage.

**More detail:** The app's interpretation table covers selected standardized terms. Coefficient size depends on input scaling. For spline distance, interpret the combined curve or distance bands rather than one number. These are fitted associations, not proof that changing a player's history, angle or distance by itself causes the stated improvement.

**Also called / searchable fields:** coefficient; model coefficient interpretation; model_interpretation; interpretation

**Related:** Odds multiplier and log odds; Feature and standardized input; Association versus cause and effect

### Odds multiplier and log odds

Odds are probability divided by one minus probability. An odds multiplier scales those odds when a model input changes on its fitted scale.

**Example:** A 50% probability has odds 0.5 ÷ 0.5 = 1. Doubling the odds gives 2, which converts to 2 ÷ (1 + 2) = 66.7% probability, not 100%.

**More detail:** Log odds are the natural logarithm of odds. The logistic model works on this scale; exponentiating a coefficient produces its odds multiplier. A multiplier above 1 indicates higher modeled odds, below 1 lower odds. It is not a direct multiplier on probability, points or causal impact.

**Also called / searchable fields:** odds; odds multiplier; odds_multiplier; log odds; logit; exp(coefficient)

**Related:** Coefficient: a model association; Mean log loss: penalty for the actual result; Make probability: chance of a successful shot

### L2 regularization

Regularization discourages overly large fitted coefficients. It helps a model avoid fitting every quirk of its training data.

**Example:** A model that memorizes small training patterns can look strong on those shots and perform poorly on later ones. Regularization limits that tendency.

**More detail:** L2 penalizes the sum of squared coefficients. The logistic model uses C = 1.0, an inverse-strength setting in its implementation. This training penalty differs from the scenario's uncertainty penalty and L1 movement budget. Regularization can improve stability but does not guarantee calibration or remove missing-variable bias; held-out evaluation is still needed.

**Also called / searchable fields:** L2; regularization; penalty; C; overfitting

**Related:** Feature and standardized input; Training, model selection, held-out and final test; Uncertainty penalty / risk

### Prespecified hypotheses / H1–H4

A hypothesis is a research claim to examine. Prespecified means the claim and its check were set out in the protocol rather than invented after inspecting the result.

**Example:** H1 examines the distance pattern; H2 compares corner-three and paint estimates; H3 checks shrinkage of small zone samples; H4 compares model error with a simpler zone baseline.

**More detail:** Supported means the reported check matched the claim under this analysis, not that it is universally true. The H1 result uses Spearman's rank correlation, a measure of whether two quantities tend to rise or fall together; values range from −1 to +1. A negative distance correlation means estimated chances tend to fall as distance rises across the bands. Read the specific method and held-out result before interpreting Status.

**Also called / searchable fields:** hypothesis; hypotheses; hypothesis_results; prespecified hypotheses; H1; H2; H3; H4; held-out result; supported; Spearman; rho; ρ; method; result

**Related:** Association versus cause and effect; Nonlinear spline and distance bands; Model validation and evaluation season

### Validation-score differences

A score difference compares two models' errors on the same evaluated shots. Lower Brier score and log loss are better, so the subtraction order matters.

**Example:** A baseline Brier score of 0.2400 minus a selected-model score of 0.2300 is +0.0100 improvement. Reversing that subtraction gives −0.0100 for the same comparison.

**More detail:** The app's caption subtracts the selected score from the global baseline. In the saved test_confidence_intervals, brier_difference instead subtracts the Zone shrinkage baseline's error from the selected model's error, so negative favors the selected model. An interval including zero does not clearly separate the errors under resampling. A small error improvement is not a direct estimate of extra basketball points.

**Also called / searchable fields:** brier_difference; score difference; Brier difference; model improvement

**Related:** Mean Brier score: squared probability error; 95% interval / CI and uncertainty; Baseline, global rate and zone shrinkage

## Methods & data

### Coverage, missing data and limitations

Coverage describes which games and attempts are actually available and included. The cohort is the group of records included in the analysis. Missing data means some information was absent or unusable.

**Example:** A team can have played 35 games but only 32 may appear in the available shot records. Games represented reports the covered games rather than filling in the missing ones.

**More detail:** The project checks the available source, valid fields and Division I membership, then records exclusions. A large final sample is not proof of a complete season. Missingness can affect comparisons if omitted games or shots differ systematically. limitations records practical boundaries, including incomplete context and imperfect geometry. Blank map cells can also result from the display threshold, which is different from missing source records.

**Also called / searchable fields:** coverage; cohort; missing data; missingness_after_cleaning; limitations; partial source coverage; source games; missing-data policy; unavailable games

**Related:** Data audit, cleaning and duplicate checks; Minimum attempts per model-map cell; Defender distance, fatigue, shot clock and play type

### Defender distance, fatigue, shot clock and play type

Several important influences on a shot are not reliably attached to these NCAA shot records. The app cannot fully explain them just from a location and an outcome.

**Example:** An open three and a closely contested three can share a location but have different chances. Without defender distance, the model may not distinguish them adequately.

**More detail:** Fatigue, time remaining on the shot clock, type of play and passing alternatives can also change shot quality. The app does not claim to measure them or use final-game outcomes as substitutes. Exact second-chance sequences remain unavailable in Team context. Use these gaps to frame video-review questions and to qualify predictions, rather than treating the estimates as complete descriptions of play.

**Also called / searchable fields:** defender distance; defensive pressure; fatigue; shot clock; shot-clock pressure; play type; play calls; passing; unavailable context; second-chance sequences

**Related:** Shot availability and unchanged efficiency; Player development and video-review prompts; Data leakage and future information

### SportsDataverse, NCAA-native and hoopR

SportsDataverse distributes the historical basketball files used here. NCAA-native describes the shot source; hoopR.mbb supplies the separate box-score source used for Team context.

**Example:** Data associated with an R package can still be read and analyzed in Python when it is distributed in a standard format. This project runs in Python.

**More detail:** A publisher makes files available. Upstream means an earlier source in the data pipeline; an adapter converts its records into the fields used here. Geometry-inferred means values or zones are assigned from chart-position rules rather than directly verified shot labels. Source provenance records origin and version. source_files lists names, sizes, hashes and URLs. CourtSense adds checks and analysis and credits the original records in Methods & downloads.

**Also called / searchable fields:** SportsDataverse; NCAA-native; source; source_documentation; hoopR; hoopR.mbb; R; Python; publisher; upstream; adapter; geometry-inferred; source_file; source_files; source provenance; url

**Related:** Data audit, cleaning and duplicate checks; CC BY 4.0: attribution license; Reproducibility and quality checks

### Data audit, cleaning and duplicate checks

A data audit records what was checked, removed or retained before modeling. Cleaning makes fields consistent and rejects records that fail the project's rules.

**Example:** Two attempts can have identical chart fields without being the same event. Because native records lack an event ID, the current builder preserves exact matching rows instead of silently deleting them.

**More detail:** The project checks geometry-inferred values, outcomes, zones, identifiers, coordinates, Division I membership and box-score reconciliation. The saved audit also contains legacy cleaning-stage counters, including earlier duplicate removal; these should not be read as the current full cohort's policy or counts. Use the snapshot season summary for the displayed cohort. Exclusion reasons may overlap. An audit reduces known errors but does not establish perfect tracking or complete coverage.

**Also called / searchable fields:** audit; cleaning; coding guide; inclusion rules; exclusions; duplicate; deduplication; rows_before; rows_after_exact_deduplication; exact_duplicate_rows_removed; rows_excluded_from_model; rows_in_model; excluded_by_missing_or_invalid_field; coordinate_rows; shooters; team_rows

**Related:** Coverage, missing data and limitations; ID, player keys and game identifiers; Reconciliation and joining shot data to box scores

### Reconciliation and joining shot data to box scores

Joining links related records, such as a team's shot data and its game box score. Reconciliation checks that their key counts agree before using them together.

**Example:** A consistent total-score check is 2 × field goals made + three-pointers made + free throws made. The extra three-pointer term supplies the third point for each made three.

**More detail:** 3PA means three-point attempts and 3PM means three-point makes. The context builder checks field goals and threes against the shot records and requires both teams' valid boxes. This can exclude games that remain usable in the shot explorer, so coverage differs. threes in the aggregate context snapshot counts three-point attempts. A matching join does not reconstruct every possession sequence or verify neutral-site labels.

**Also called / searchable fields:** reconciled; reconciliation; join; matched games; field_goals_attempted; field_goals_made; three_point_field_goals_attempted; three_point_field_goals_made; 3PA; 3PM; threes

**Related:** Team context: the whole offense; Point value: two or three points; Coverage, missing data and limitations

### ID, player keys and game identifiers

An ID is a code used to identify a record or entity. Player keys, team IDs and game IDs let the project group the right attempts together.

**Example:** contest_id identifies a game. player_key identifies a player within the source's relevant season context. Similar player names alone are not enough to guarantee a match.

**More detail:** Source player IDs often change between seasons, so the app deliberately avoids automatic cross-season name merging. shot_uid identifies a cleaned historical attempt. NCAA and ESPN ID fields connect source systems where mappings are available. In the hypothesis table ID instead means a claim label such as H1. An identifier is not a statistic or evidence of performance.

**Also called / searchable fields:** ID; id; identifier; player_key; contest_id; game_id; team_id; shooter_id; ncaa_team_id; espn_team_id; espn_game_id; shooter_player_id; shooter_clean_name; shot_uid; source IDs

**Related:** Season and ending-year codes; Player development and video-review prompts; Data audit, cleaning and duplicate checks

### Saved snapshot, freeze, run and version

A snapshot is a saved set of data and analysis results built at a particular time. The app displays this saved research rather than fetching a live feed for every visit.

**Example:** Changing a team filter selects different rows from the saved dataset; it does not download today's game results or retrain the model.

**More detail:** run_id identifies the saved analysis build. The app version describes the interface release, and protocol_version describes the analysis rules. These can change independently. A freeze fixes the data or procedure for the intended evaluation. The build timestamp says when results were produced, not when every game was played. Reproducibility requires keeping the version, inputs and configuration together.

**Also called / searchable fields:** snapshot; saved snapshot; analysis snapshot; live data feed; run; run_id; app version; protocol_version; version; release

**Related:** Training, model selection, held-out and final test; UTC and game dates; SHA-256 / sha256: file fingerprints; Reproducibility and quality checks

### UTC and game dates

UTC stands for Coordinated Universal Time, a shared reference time. generated_utc records when the analysis was built; game_date describes a recorded game's date.

**Example:** A build timestamp ending in Z uses UTC. It may correspond to a different local calendar date near midnight in your time zone.

**More detail:** Build time and game time are different facts. The player-history calculation uses earlier UTC dates and excludes the current date's outcomes. This conservative ordering prevents same-date results from being treated as earlier information. Date ranges in a summary describe the included records, not a claim that every game between them is present.

**Also called / searchable fields:** UTC; generated_utc; game_date; timestamp; built date; date; date_start; date_end

**Related:** Earlier player history and history size; Saved snapshot, freeze, run and version; Coverage, missing data and limitations

### SHA-256 / sha256: file fingerprints

A SHA-256 hash is a digital fingerprint of file contents. It helps check whether two copies contain the same bytes.

**Example:** If a dataset changes, its hash normally changes too. data_sha256 and config_sha256 identify the data and configuration used for the saved analysis.

**More detail:** A byte is a unit of stored data; bytes records file size. Hashes help detect accidental changes and reproduce an analysis with matching inputs. They do not prove that the source data is accurate, that a prediction is good, or that a study is causal. A Git commit identifier is a separate repository identifier and should not be confused with the saved data hash.

**Also called / searchable fields:** SHA-256; SHA256; sha256; data_sha256; config_sha256; checksum; hash; fingerprint; bytes; file

**Related:** Reproducibility and quality checks; Configuration, settings and model specification

### Configuration, settings and model specification

Configuration records the analysis choices: seasons, candidate models, prior weights, resampling settings and scenario limits. Model specification explains the fitted model and its targets.

**Example:** The saved case-study team can be Ohio State while you are viewing another team in the app. The stored report scenario and the interactive scenario are separate calculations.

**More detail:** config and model_spec appear in the JSON. settings stores a saved scenario's controls; season_summary gives counts by season; table holds rows such as zone estimates. notes in the JSON records analysis choices. In the prospective CSV, notes instead records non-identifying protocol deviations: occasions when collection departed from its planned rules. Inspect context and data version before comparing builds; identical labels do not guarantee identical settings.

**Also called / searchable fields:** config; configuration; settings; model_spec; notes; protocol deviation; case_study_team; season_summary; teams; players; seasons; table

**Related:** Saved snapshot, freeze, run and version; Scenario, retrospective and conditional estimate; Training, model selection, held-out and final test

### Random seed and repeatability

A random seed fixes the starting state of a random calculation, allowing repeated runs to use the same resampling draws when the data and method are unchanged.

**Example:** The main scenario uses seed 42. Running the same calculation with the same records, controls and software should produce the same bootstrap sequence.

**More detail:** The number 42 has no basketball meaning. A different seed can slightly change resampling estimates. Reproducibility also depends on matching the data, configuration and software versions; a seed alone is insufficient. Changing teams or controls appropriately changes results even when the seed is fixed.

**Also called / searchable fields:** seed; random seed; random state; 42; reproducibility; repeatable

**Related:** Bootstrap, game resampling and clusters; SHA-256 / sha256: file fingerprints; Configuration, settings and model specification

### Prospective validation, protocol and analyzer

Prospective means collecting new observations after fixing the plan. The project provides a protocol, blank recording template and analyzer for a possible future validation study.

**Example:** A future participant could record attempts using the template, then the analyzer could compare frozen probabilities with new outcomes. The example row must be removed before collecting real data.

**More detail:** No real prospective experiment has been conducted or reported. The protocol specifies anonymous participant codes, sessions, strategy blocks and recording order. Session-cluster intervals keep observations from the same session together. Historical scenarios are not substitutes for an experiment. The analyzer can process future data, but it cannot create genuine results without observations.

**Also called / searchable fields:** prospective; prospective validation; protocol; validation protocol; anonymous shot template; prospective outcome; analyzer; post-freeze protocol; real experiment

**Related:** Anonymous participant codes and shot IDs; Session, blocks and attempt order; Current versus recommended strategy blocks; 95% interval / CI and uncertainty

### CC BY 4.0: attribution license

CC BY 4.0 means Creative Commons Attribution 4.0. It is the license cited for the box-score source used in Team context.

**Example:** When presenting or redistributing derived context material, retain appropriate credit to the source and describe CourtSense's joins, checks and aggregation.

**More detail:** A license describes permissions and conditions for using material; it does not certify accuracy or apply automatically to every other dataset in the project. The Methods page links the relevant source and license. Consult those source-specific terms when reusing data. CourtSense's analysis and interface are distinct from the original records.

**Also called / searchable fields:** CC BY 4.0; Creative Commons; attribution; license; licence

**Related:** SportsDataverse, NCAA-native and hoopR; Team context: the whole offense

### Reproducibility and quality checks

Reproducibility means someone can rerun the documented method with matching inputs and obtain the same analysis. Quality checks catch specific problems before results are used.

**Example:** The project saves raw-file fingerprints, configuration, season splits and seeds, then checks the data snapshot and runs automated code tests.

**More detail:** Tests can verify calculations, chronology, input handling and app behavior. They do not prove the original source is complete or that a scenario will work in a real game. Matching data, software and analysis rules matters alongside a fixed seed. A reproducible biased calculation is still biased; use the audit and limitations to assess the evidence as well as the build process.

**Also called / searchable fields:** reproducibility; reproduce; quality checks; tests; verification; build; analysis build

**Related:** SHA-256 / sha256: file fingerprints; Random seed and repeatability; Data audit, cleaning and duplicate checks; Training, model selection, held-out and final test

### Minimum, maximum and percentiles

A minimum is the smallest value and a maximum is the largest. A percentile marks a position in sorted observations; the 50th percentile is the median.

**Example:** If distances are 2, 4, 6, 8 and 10 feet, the minimum is 2, maximum is 10 and median is 6. Half the observations are at or below the median position.

**More detail:** The audit can include distance summaries labeled 25%, 50% and 75%. These are quartile positions in a distribution, not shooting percentages. A percentile's value retains the original measurement's units, such as feet. The bootstrap uses its 2.5th and 97.5th percentiles for reported intervals. A map-cell minimum is instead a display-count threshold.

**Also called / searchable fields:** min; max; minimum; maximum; 25%; 50%; 75%; percentile; median; quartile

**Related:** Coordinates, distance, angle and feet; Bootstrap, game resampling and clusters; Minimum attempts per model-map cell

## Downloads & field names

### Anonymous participant codes and shot IDs

participant_code labels a person in a prospective study without writing their name. shot_id uniquely labels an attempt.

**Example:** P001 can identify one participant; S01-B01-001 can identify a particular attempt. Reusing a shot_id for two shots would make record tracking ambiguous.

**More detail:** Codes reduce direct identification but do not automatically make all data anonymous in every context. The provided template avoids asking for names. Use consistent codes for the same participant within the intended study. Historical player names in the public source are separate from these prospective codes. The supplied example row is illustrative and must be deleted before analysis of real observations.

**Also called / searchable fields:** participant_code; participant; anonymous; shot_id; personal information

**Related:** Prospective validation, protocol and analyzer; Session, blocks and attempt order; ID, player keys and game identifiers

### Session, blocks and attempt order

A session groups attempts collected on one recording occasion. A block groups consecutive attempts under one assigned condition. Order fields record when blocks and shots occurred.

**Example:** In session S01, block B01 might come first, with attempt_order 1, 2, 3. Another block can then use the alternative strategy.

**More detail:** session_id and block_id connect related rows; block_order and attempt_order preserve sequence. This matters because fatigue or practice can change outcomes over time. The prospective analyzer clusters uncertainty by session rather than pretending every shot is independent. These fields belong to the new-data template, not the historical game filters.

**Also called / searchable fields:** session_id; block_id; block_order; attempt_order; session; block; order

**Related:** Current versus recommended strategy blocks; Bootstrap, game resampling and clusters; Prospective validation, protocol and analyzer

### Current versus recommended strategy blocks

strategy labels which planned shot-selection condition was used in a prospective block. It does not record whether a shot was made.

**Example:** The template requires exactly current or recommended. A current block follows the existing mix; a recommended block follows the proposed mix. made still records each shot's 0/1 outcome.

**More detail:** Counterbalanced order varies which condition comes first, reducing its link to fatigue or practice effects. Randomized assignment uses chance to choose the order. Adherence means how closely the actual attempts followed the assigned mix. Read the protocol for assignment rules before collecting data. A strategy label alone cannot establish a fair causal comparison; execution, order and real new observations matter. No real strategy-block results are claimed here.

**Also called / searchable fields:** strategy; current; recommended; alternative; assigned strategy; counterbalanced

**Related:** Session, blocks and attempt order; Prospective validation, protocol and analyzer; Association versus cause and effect

### CSV: spreadsheet-friendly tables

CSV stands for comma-separated values. It stores a plain table that Excel, Google Sheets and Python can read. Each row is a record and each column is a field.

**Example:** In a zone-summary CSV, count is attempts, fg_pct = 0.45 means 45%, and expected_pps = 1.10 means 1.10 predicted points per attempt.

**More detail:** The app's formatted table may show friendlier headings than the CSV's code names. Search an exact exported column here to learn its meaning. A scenario CSV uses raw zone codes and decimal shares. A player-trend CSV includes dates and per-game totals. The prospective template is for recording new attempts, not historical results. Downloading creates a file; it does not send information to the project owner.

**Also called / searchable fields:** CSV; comma-separated values; download selected zone summary; download scenario table; download player game trend; shot template; column; row; export; download

**Related:** FG% / fg_pct: field-goal percentage; Share of attempts: a zone's part of the mix; JSON: saved analysis results; Feedback notes, issues and GitHub

### JSON: saved analysis results

JSON stands for JavaScript Object Notation. It stores labeled values, lists and nested groups, which lets the saved analysis include more structure than one spreadsheet table.

**Example:** model_comparison lists model names and scores. scenario groups a saved case-study scenario with its settings and zone table. audit groups data-quality checks.

**More detail:** The file can be read with a text editor or Python; JavaScript programming is not required. Its saved case study need not match your current interactive filters. True and false are boolean values such as feasibility; numbers retain their units from the relevant definition. Search field names in this guide before interpreting decimal rates or interval bounds. JSON itself is a file format, not a prediction method.

**Also called / searchable fields:** JSON; JavaScript Object Notation; saved analysis results; analysis results; data dictionary

**Related:** Configuration, settings and model specification; Data audit, cleaning and duplicate checks; Saved snapshot, freeze, run and version; CSV: spreadsheet-friendly tables

### PDF and the research report

PDF stands for Portable Document Format. The research report is a fixed-layout document explaining the question, data, methods, results and limitations.

**Example:** Use the report when you need the research reasoning behind the dashboard rather than just one team's current view.

**More detail:** The report reflects the saved analysis build. Its case-study numbers can differ from a newly selected team or customized scenario in the app. The printable team report card is downloaded as HTML; your browser's Print → Save as PDF creates a PDF copy of that handout. A report's format does not make its conclusions stronger than the underlying evidence.

**Also called / searchable fields:** PDF; Portable Document Format; research report; download research report; print

**Related:** Compare teams and printable report cards; Saved snapshot, freeze, run and version; HTML and browser report cards

### PPTX and the presentation

PPTX is the PowerPoint presentation file format. The project presentation provides a slide-based walkthrough of the research and results.

**Example:** Open the deck in PowerPoint or a compatible presentation app to explain the project to a class or portfolio audience.

**More detail:** The slides summarize the saved analysis rather than live-filtered app results. Use the research report for fuller methods and caveats. Images and displayed numbers in the deck do not automatically change when a sidebar selection changes. Avoid presenting the historical scenario as a completed prospective experiment.

**Also called / searchable fields:** PPTX; PowerPoint; presentation; download presentation; slides

**Related:** PDF and the research report; Saved snapshot, freeze, run and version; Prospective validation, protocol and analyzer

### HTML and browser report cards

HTML stands for HyperText Markup Language, the format browsers use to display pages. The team report card is a self-contained HTML file.

**Example:** Download a report card, open it in a browser, and choose Print → Save as PDF to make a shareable handout.

**More detail:** Self-contained means the handout includes its own content and styling rather than requiring the CourtSense app to render it. It contains the team and season shown when the report was generated. A download is a snapshot, so later filter changes do not update the file you already saved. HTML is a document format, not a measure of model quality.

**Also called / searchable fields:** HTML; HyperText Markup Language; self-contained HTML; browser; report card file

**Related:** Compare teams and printable report cards; PDF and the research report; Saved snapshot, freeze, run and version

### Feedback notes, issues and GitHub

A feedback note records what you want improved or what went wrong. The app lets you download a note to share with the project owner.

**Example:** Describe the page, selection, problem and expected behavior. Downloading the note does not send it automatically; share the file with the owner separately.

**More detail:** GitHub hosts the project's code repository, which is private. A repository is a collection of versioned project files. An issue is a tracked bug or request in that system; access depends on repository permissions. Visitors do not need a GitHub account to create the downloadable note. Avoid including private information in a screenshot or note you plan to share.

**Also called / searchable fields:** feedback; feedback note; GitHub; issue; repository; download feedback note; bug; feature request

**Related:** CSV: spreadsheet-friendly tables; Saved snapshot, freeze, run and version
