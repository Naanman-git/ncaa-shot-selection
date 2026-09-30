"""Plain-language help for first-time visitors to CourtSense."""

GUIDE_TOPICS = [
    ("Start here · the one-minute tour", """
CourtSense explores **where NCAA Division I men's teams shoot**, how likely those
shots are to go in, and what a small change in shot selection could mean.

1. In **Choose your view**, pick a season, team and optionally a player.
2. Open **Court explorer** to see where shots happen and what they are worth.
3. Try **Compare teams** and download a printable team report card.
4. Open **Player development** for a player's game-by-game trends.
5. Explore **Shot-mix scenarios** and their uncertainty, or **Team context** for whole-offense estimates.
6. Open **Model validation** to check prediction quality on later games.
7. Use **Story mode** for a six-chapter walkthrough with the selected team or player.
8. Visit **Methods & downloads** for reports, version details and a feedback note.

Use the arrow at the top of this sidebar to collapse it. Reopen it with the
arrow in the top-left corner. Each topic below can also be opened or closed.
"""),
    ("Attempts, makes and field-goal % · fg_pct", """
**Attempt** means a recorded two-point or three-point shot, whether made or missed.
**Makes** counts the shots that went in. Free throws are excluded.

**Field-goal percentage (FG%, fg_pct, raw_fg)** is makes divided by attempts.
Making 45 of 100 shots gives **45%**. An exported value of **0.45 means 45%**.
A two-pointer and a three-pointer each count as one attempt in this percentage.

**Games represented** counts the distinct games in the selected data; coverage
may not include every game played. **Shot share** is the fraction of attempts
from a zone: 30 out of 100 attempts means a 30% share.
"""),
    ("Make probability · how likely a shot is to go in", """
**Make probability** is the model's estimated chance of a successful shot.
For example, 40% means about 40 makes out of 100 similar attempts if the
estimate is well calibrated; it does not promise the next shot will go in.

The estimate uses location, distance, angle, zone and the player's earlier
shooting history. **Observed** describes what actually happened;
**predicted** describes the model's estimate.
"""),
    ("Points per attempt · pps and expected points", """
**Observed points per attempt (pps, observed_pps)** is points scored on recorded
field goals divided by attempts. Scoring 110 points from 100 attempts gives **1.10**.

**Predicted points per attempt (expected_pps)** averages each shot's estimated
make probability multiplied by its two- or three-point value.
A three-pointer with a 40% chance is worth **0.40 × 3 = 1.20 expected points**;
a two-pointer with a 50% chance is worth **0.50 × 2 = 1.00**.

These are averages, not points guaranteed on a single shot. Free throws,
turnovers and offensive rebounds are not included, so this is not points per possession.
"""),
    ("Court maps, colour scales and zones", """
Each small square groups recorded shots from a similar court location.
Hover over a coloured square to see its value and number of attempts.

- **Attempts:** darker squares contain more recorded shots.
- **Make probability:** darker squares have a higher average predicted chance of a make.
- **Points / attempt:** darker squares have higher average predicted points.

Read the separate scale below each map. Count scales can change with the selection,
so the same colour across different teams does not necessarily mean the same count.
Blank cells have no eligible data or too few attempts; blank does not mean a 0% chance.
The **minimum attempts** setting hides small samples in the two prediction maps.

**At the rim:** near the basket. **Paint:** other shots inside the lane.
**Midrange:** other two-point shots. **Corner three:** threes near the baseline
corners. **Above-break three:** threes around the rest of the arc.
Zone labels come from the source's court geometry and can be imperfect.
"""),
    ("Shot-mix scenarios · shares, pp and limits", """
**Shot mix** is how a team's attempts are spread across zones. The scenario
explores moving a limited share of attempts while assuming zone efficiency stays similar.

**Percentage points (pp):** increasing a zone from 20% to 25% is a 5-point shift.
**Maximum shift per zone** limits each zone's increase or decrease.
**Total mix movement** adds all increases and decreases: moving 5 points from one
zone to another uses 10 points of movement. **Three-point share cap** limits
the fraction of attempts that are threes.

**Estimated change / 100 attempts** expresses the estimated scoring difference
over 100 shots. It does not predict a team's final score or prove a strategy will work.
An **infeasible** scenario means the selected limits cannot all be satisfied.
"""),
    ("Uncertainty, adjusted rates and scenario exports", """
**Adjusted make rate (shrunk_fg)** blends a zone's recorded make rate with
an earlier pooled rate. Small samples are pulled more toward that pooled rate
so a few lucky shots have less influence. This adjustment is called **shrinkage**.

**Estimated points (ep)** in the scenario equal that adjusted rate times the shot value.
**ep_low / ep_high** are the lower and upper resampling bounds for that estimate.
**current_share / recommended_share** describe the recorded and scenario shot mix.
**Eligible** means a zone has enough observations to allow its mix to change.

The **95% interval** summarizes variation when the analysis resamples whole games.
If the change interval crosses zero, those resampled estimates include both gains
and losses. It does not include every source of uncertainty, such as how defenders
would react. A higher **uncertainty penalty** favors more certain zone estimates;
it is not a confidence percentage.
"""),
    ("Model validation · Brier score, log loss and calibration", """
Validation checks predictions against outcomes in later games. The evaluation
season selector controls these results; team and player filters do not change them.

**Mean Brier score** averages the squared gap between the predicted probability
and the actual result (made = 1, missed = 0). Lower is better; 0 is perfect.
For a 70% prediction, a make contributes (0.70 − 1)² = 0.09;
a miss contributes (0.70 − 0)² = 0.49.

**Mean log loss** measures the penalty for the probability assigned to the result
that happened. It penalizes very confident wrong predictions especially strongly.
Lower is better; 0 is perfect. These scores are not shooting percentages and their
numerical sizes are not directly comparable to each other.

**Calibration** asks whether predicted chances match actual make rates.
If shots predicted at 40% go in about 40% of the time, that group is well calibrated.
The diagonal on the chart represents perfect agreement.

A **baseline** is a simple reference model. The global-rate baseline assigns the
same training-data make rate to every shot. Compare scores on the same evaluation
shots. A **hypothesis** is a research claim tested against the data;
a **coefficient** describes a model association, not proof of cause and effect.
"""),
    ("Possessions, team context and player trends", """
**Points per estimated possession** includes the team's total score, including free
throws. Estimated possessions account for shots, offensive rebounds, turnovers
and free-throw attempts. They are approximations from box scores, not counted play sequences.
The **Team context** page explains the formula and shows home/away designations.
Neutral-site games can still carry a home/away designation in the source.

**Player development** shows one player's selected season. The recent five-game
average divides all points by all attempts in that window, so small games do not
receive equal weight to large ones. Practice prompts suggest video-review questions;
they are not validated training advice. Source player IDs usually change between
seasons, so cross-season identities are not automatically merged.

**Sample support** labels summarize observations: usable = at least 30 attempts in
5 games; broader = at least 100 attempts in 10 games. They do not measure the
probability that a recommendation will succeed.
"""),
    ("What to trust · methods and downloads", """
The project trains on 2022–23 and 2023–24, selects its model on 2024–25,
and uses 2025–26 for the final evaluation. Earlier player results may update
shooting history; current and future outcomes are excluded from a shot's inputs.

This is evidence about recorded shots. Defender distance, fatigue, shot-clock
pressure and available passing options are not all captured. Small samples and
missing source games can affect conclusions.

In **Methods & downloads**, get the report for the research detail, the presentation
for a walkthrough, and the saved analysis results for the numbers behind the app.
The prospective protocol and blank template describe a possible future experiment;
no real prospective experiment results are claimed.
"""),
]


def render_beginner_guide(st):
    """Render inside the sidebar; search reveals all matching topics."""
    st.subheader("Beginner’s guide")
    st.caption("New to basketball analytics? Open a topic or search for a term.")
    query = st.text_input("Find a term or topic", placeholder="Try fg_pct, pps, probability…", key="guide_search").strip().casefold()
    matches = [(title, body) for title, body in GUIDE_TOPICS
               if not query or query in (title + " " + body).casefold()]
    if not matches:
        st.info("No matching topic. Try a shorter term, or clear the search to see the full guide.")
    for index, (title, body) in enumerate(matches):
        with st.expander(title, expanded=bool(query) or index == 0):
            st.markdown(body)
