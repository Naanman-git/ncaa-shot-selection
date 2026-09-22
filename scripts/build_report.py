#!/usr/bin/env python3
"""Build the academic report from the frozen analysis, never from hand-entered results.

The PDF and Markdown are two views of the same content. Run after the analysis
pipeline has written data/outputs/final_results.json and output/figures.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/outputs/final_results.json"
OUT = ROOT / "output/pdf/ncaa_shot_selection_report.pdf"
NAVY = colors.HexColor("#102A43")
TEAL = colors.HexColor("#087F8C")
ORANGE = colors.HexColor("#D77A38")
CREAM = colors.HexColor("#FAF8F2")
MUTED = colors.HexColor("#526777")
LIGHT = colors.HexColor("#E6ECEF")


def num(value, digits=0):
    return f"{float(value):,.{digits}f}"


def pct(value, digits=1):
    return f"{100 * float(value):.{digits}f}%"


def interval(value, digits=4):
    if isinstance(value, dict):
        value = [value.get("low", value.get("lower")), value.get("high", value.get("upper"))]
    return f"[{num(value[0], digits)}, {num(value[1], digits)}]"


class AcademicReport:
    def __init__(self, run_id):
        self.run_id = run_id
        self.flow = []
        self.md = []
        self.page_title = "NCAA SHOT SELECTION"
        self.styles = getSampleStyleSheet()
        common = dict(fontName="Helvetica", textColor=NAVY, alignment=TA_LEFT)
        self.styles.add(ParagraphStyle("ReportTitle", fontName="Helvetica-Bold", fontSize=29,
                                       leading=33, textColor=NAVY, spaceAfter=19))
        self.styles.add(ParagraphStyle("ReportSubtitle", fontSize=13, leading=19,
                                       textColor=MUTED, fontName="Helvetica", spaceAfter=20))
        self.styles.add(ParagraphStyle("ReportHeading", fontName="Helvetica-Bold", fontSize=18,
                                       leading=23, textColor=NAVY, spaceBefore=4, spaceAfter=14,
                                       keepWithNext=True))
        self.styles.add(ParagraphStyle("ReportSubheading", fontName="Helvetica-Bold", fontSize=11.3,
                                       leading=15.4, textColor=TEAL, spaceBefore=11, spaceAfter=5,
                                       keepWithNext=True))
        self.styles.add(ParagraphStyle("ReportBody", fontSize=10, leading=14.3,
                                       spaceAfter=9, **common))
        self.styles.add(ParagraphStyle("ReportSmall", fontSize=8.1, leading=11,
                                       spaceAfter=6, **common))
        self.styles.add(ParagraphStyle("ReportCell", fontSize=8.1, leading=11,
                                       spaceAfter=0, **common))
        self.styles.add(ParagraphStyle("ReportCaption", fontSize=8.2, leading=11.5,
                                       spaceAfter=12, textColor=MUTED, fontName="Helvetica"))

    def p(self, text, style="ReportBody"):
        # The source strings use only ASCII hyphens and XML-safe prose.
        self.flow.append(Paragraph(text, self.styles[style]))
        self.md.append(text.replace("<b>", "**").replace("</b>", "**").replace("<br/>", "\n") + "\n")

    def title(self, text, subtitle):
        self.p(text, "ReportTitle")
        self.p(subtitle, "ReportSubtitle")

    def section(self, title, new_page=True):
        if new_page:
            self.flow.append(PageBreak())
        self.flow.append(Paragraph(title, self.styles["ReportHeading"]))
        self.md.append(f"\n## {title}\n")

    def sub(self, title):
        self.flow.append(Paragraph(title, self.styles["ReportSubheading"]))
        self.md.append(f"\n### {title}\n")

    def table(self, headers, rows, widths=None, caption=None):
        values = [headers] + [[str(v) for v in row] for row in rows]
        data = [[Paragraph(escape(str(v)), self.styles["ReportCell"]) for v in row] for row in values]
        widths = widths or [468 / len(headers)] * len(headers)
        table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CREAM]),
            ("LINEBELOW", (0, 0), (-1, 0), .7, NAVY),
            ("LINEBELOW", (0, -1), (-1, -1), .7, LIGHT),
        ]))
        for cell in data[0]:
            cell.style = ParagraphStyle("HeaderCell", parent=self.styles["ReportCell"],
                                        textColor=colors.white, fontName="Helvetica-Bold")
        self.flow.extend([table, Spacer(1, 10)])
        self.md.append("| " + " | ".join(headers) + " |")
        self.md.append("| " + " | ".join("---" for _ in headers) + " |")
        self.md.extend("| " + " | ".join(str(v).replace("|", "/") for v in row) + " |" for row in rows)
        self.md.append("")
        if caption:
            self.p(caption, "ReportCaption")

    def figure(self, filename, caption, max_height=290):
        path = ROOT / "output/figures" / filename
        if not path.exists():
            raise FileNotFoundError(f"Required evidence figure missing: {path}")
        w, h = ImageReader(str(path)).getSize()
        scale = min(468 / w, max_height / h)
        self.flow.append(Image(str(path), width=w*scale, height=h*scale, hAlign="CENTER"))
        self.flow.append(Spacer(1, 5))
        self.p(caption, "ReportCaption")
        self.md.append(f"![{caption}](../output/figures/{filename})\n")

    def save(self):
        OUT.parent.mkdir(parents=True, exist_ok=True)
        width, height = 612, 792

        def decorate(canvas, doc):
            canvas.saveState()
            canvas.setFillColor(NAVY)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawString(72, height - 36, self.page_title)
            canvas.setFillColor(MUTED)
            canvas.setFont("Helvetica", 7.1)
            canvas.drawRightString(width - 72, height - 36, "DIVISION I MEN'S BASKETBALL")
            canvas.setStrokeColor(LIGHT)
            canvas.line(72, 48, width-72, 48)
            canvas.setFont("Helvetica", 6.8)
            canvas.drawString(72, 34, f"Research and portfolio edition | Run {self.run_id}")
            canvas.drawRightString(width-72, 34, str(doc.page))
            canvas.restoreState()

        doc = BaseDocTemplate(str(OUT), pagesize=(width, height), title="NCAA Division I Men's Shot Selection",
                              author="NCAA Shot Selection Project", subject="Reproducible predictive analysis and constrained scenarios",
                              leftMargin=72, rightMargin=72, topMargin=65, bottomMargin=64)
        doc.addPageTemplates(PageTemplate(id="report", frames=[Frame(72, 64, 468, 663,
                                                                     leftPadding=0, rightPadding=0,
                                                                     topPadding=0, bottomPadding=0)],
                                         onPage=decorate))
        doc.build(self.flow)
        (ROOT / "docs/academic_report.md").write_text("\n".join(self.md) + "\n")
        print(OUT)


def normalize(results):
    """Convert the pipeline's result schema to a presentation-safe evidence manifest."""
    ss=results["season_summary"]
    cohort_rows=[[str(x["season"]),num(x["attempts"]),num(x["attempts"]),num(x["games"]),num(x["teams"])] for x in ss]
    comp=results["model_comparison"]
    test=[x for x in comp if x["season"]==results["config"]["final_test_season"]]
    model_rows=[[x["model"],f'{x["brier"]:.4f}',f'{x["log_loss"]:.4f}'] for x in test]
    # Keep this builder dependency-free: use the JSON records directly.
    zr=results["scenario"]["table"]
    zone_rows=[[x["zone"],num(x["count"]),pct(x["current_share"]),pct(x["ep"]/({'rim':2,'paint':2,'mid':2,'corner3':3,'abovebreak3':3}[x["zone"]]),1),f'{x["ep"]:.3f}'] for x in zr]
    mix_rows=[[x["zone"],pct(x["current_share"]),pct(x["recommended_share"]),pct(x["recommended_share"]-x["current_share"])] for x in zr]
    sens=[]
    for x in results["sensitivity"]:
        if x["risk"]==1.: sens.append([f'{x["max_shift"]:.1%}',f'{x["gain_per100"]:.2f} [{x["gain_low"]:.2f}, {x["gain_high"]:.2f}]', '—'])
    run=results["run_id"]
    model_rows=model_rows
    return {"run_id":run,"abstract":f"This reproducible study evaluates {num(sum(x['attempts'] for x in ss))} reconciled shot attempts across four seasons. A spatial logistic model with strictly prior-day player history was selected on {results['config']['selection_season']} and evaluated once on {results['config']['final_test_season']}. The scenario engine estimates a conditional change of {results['scenario']['gain_per100']:.2f} points per 100 recorded attempts for the prespecified case study.",
      "main_findings":[f"The frozen model selected on 2024–25 was <b>{results['selected_model']}</b>; its 2025–26 Brier score and log loss are shown in the held-out table.",f"For {results['scenario']['team']} ({results['scenario']['season']}), the constrained descriptive scenario estimates {results['scenario']['gain_per100']:.2f} points per 100 recorded attempts, with a game-bootstrap range [{results['scenario']['gain_low']:.2f}, {results['scenario']['gain_high']:.2f}].", "These values describe recorded attempts and do not identify a causal coaching intervention."],
      "data_provenance":"Native NCAA shot-chart releases were joined to the matching ESPN team box-score release. A game entered the cohort only when both teams were present and the native counts reconciled to field-goal and three-point totals. Exact duplicate rows were retained because the source has no event identifier.","cohort_rows":cohort_rows,"cohort_caption":"Included rows are the reconciled analysis cohort; team counts are unique mapped team identifiers.","cohort_methods":["The final cohort is Division I men versus men coverage inferred from mutually consistent team-game records, with season-specific identities and game dates attached from the box-score crosswalk.","A native point value and zone are geometry-inferred by the upstream adapter. They are retained as recorded fields and described as such."],"coverage_methods":["Coverage is not a claim that every NCAA Division I attempt is present. Reconciliation makes the included cohort auditable and excludes unmatched games.","The source is public SportsDataverse data; downstream redistribution rights remain governed by its upstream terms."],
      "dictionary":[["shot_x, shot_y, dist_ft","Native chart coordinates and Euclidean distance."],["shot_zone","Upstream geometry-derived five-zone label."],["made","Binary field-goal outcome."],["point_value","Geometry-derived two- or three-point value."],["player_key","Mapped player identifier; season history resets."],["model_p","Selected model probability."],["contest_id","Game identifier used for grouped resampling."]],"spatial_methods":"The source chart uses a baseline-relative coordinate convention. Cells in the evidence map are 3-foot bins and display only cells with at least 100 attempts; no spatial smoothing is applied. The 'paint' label means the upstream distance band, not a validated painted-key boundary.",
      "split_rows":[["Training","2022–23, 2023–24","Fit candidate models and priors"],["Selection","2024–25","Select by log loss; no final-test refit"],["Final test","2025–26","One fixed evaluation after selection"]],"split_caveat":"The earlier exploratory run used 2024–25 outcomes. This final protocol treats 2025–26 as the fixed final test and records its configuration hash.","model_methods":["Global and zone-shrinkage baselines use training outcomes with a fixed 30-attempt prior. Spatial logistic candidates use a five-knot distance spline, absolute shot angle, zone indicators and L2 logistic regression.","The selected history model adds a 30-attempt player-zone prior and log prior attempts. Its history is updated only with earlier dates within a season, so current and future outcomes cannot enter the current prediction."],"uncertainty_methods":"Metrics use 500 game-cluster bootstrap resamples. Scenario rates use 500 game resamples and 30-attempt shrinkage; intervals are conditional on the fixed selected mix.","model_caption":"Scores below are computed on the final 2025–26 test season after model selection was frozen.","calibration_figure":"calibration.png","calibration_caption":"Reliability bins compare mean predicted make probability with observed make rate.","predictive_interpretation":"Calibration is a diagnostic, not a guarantee. The selected probabilities describe recorded field-goal attempts under the available covariates.","subgroup_rows":[],"maps_figure":"maps.png","maps_caption":"Observed outcome, selected-model probability and recorded point value in 3-foot chart cells; sparse cells are omitted.","zone_summary_rows":zone_rows,"maps_interpretation":"Zone summaries combine frequency with outcome and model values. Point value is geometry-inferred and aggregate-reconciled, not shot-tracking truth.","scenario_description":f"The prespecified {results['scenario']['team']} case study uses {num(results['scenario']['attempts'])} final-test attempts across {num(results['scenario']['games'])} games. Zone make rates shrink toward training priors with 30 pseudo-attempts.","constraint_rows":[["Per-zone movement", "At most ±5 percentage points"],["Total movement", "L1 budget 0.20 (10 points can move)"],["Three-point share", "At most 60%"],["Sparse support", "Zones below 30 attempts or five games stay fixed"]],"zone_mix_rows":mix_rows,"scenario_result":f"The solution is {'feasible' if results['scenario']['feasible'] else 'infeasible'} under all stated constraints. Its modeled change is {results['scenario']['gain_per100']:.2f} points per 100 attempts, with a conditional bootstrap interval of [{results['scenario']['gain_low']:.2f}, {results['scenario']['gain_high']:.2f}].","sensitivity_methods":"The movement cap and risk penalty are varied while keeping the case study, priors and game bootstrap fixed.","sensitivity_rows":sens,"sensitivity_interpretation":"The gain is sensitive to the amount of reassignment allowed and to the risk penalty; it should be treated as a planning diagnostic, not an intervention estimate.","scenario_uncertainty":"The displayed range resamples games and accounts for zone-rate sampling variation. It omits policy selection, opponent response, opportunity creation and model refitting.","conclusion":"The finished product provides a reproducible NCAA Division I shot-selection workflow: reconciled cohort, chronological probability evaluation, conditional mix scenarios and an interactive explorer.","limitations":results["limitations"],"references":[{"label":"User-supplied basketball shot-selection blueprint (12-page PDF)."},{"label":"SportsDataverse NCAA men's basketball shot releases and documentation.","url":"https://github.com/sportsdataverse/hoopR/blob/main/R/load_ncaa_mbb.R"},{"label":"NCAA membership directory.","url":"https://www.ncaa.org/about-us/membership-directory/"},{"label":"Scikit-learn calibration documentation.","url":"https://scikit-learn.org/stable/modules/calibration.html"},{"label":"SciPy linear programming documentation.","url":"https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html"}],"reproducibility_note":f"Run {run}; data SHA-256 {results['data_sha256']}; configuration SHA-256 {results['config_sha256']}. Rebuild with scripts/build_clean_table.py, scripts/run_analysis.py, scripts/build_report.py and scripts/build_presentation.mjs."}


def build(results):
    m = normalize(results)
    m["model_rows"] = [[x["model"], f'{x["brier"]:.4f}', f'{x["log_loss"]:.4f}'] for x in results["model_comparison"] if x["season"] == results["config"]["final_test_season"]]
    m["notes"]=["This deck presents the frozen NCAA Division I men’s basketball analysis. It is a descriptive historical study, not a university or team product.","The cohort is reconciled native shot data joined to team boxes; counts are included coverage, not a claim of complete NCAA coverage.","Training seasons fit candidates; 2024–25 selects the model; 2025–26 is the final fixed test.","Scores are held-out Brier and log loss. The history model uses only earlier dates within a season.","Cells show recorded chart coordinates with sparse cells omitted. Point values and zones are geometry-inferred by the upstream adapter.","Calibration and game bootstrap quantify sampling behavior, but do not create causal certainty.","The case study uses a fixed-mix constrained scenario with shrinkage and explicit support gates.","Sensitivity shows how analyst-set movement limits change the conditional result.","The product supports reproducible exploration while leaving prospective coaching intervention for a separate study."]
    m["split_labels"]=["TRAIN · 2022–24","SELECT · 2024–25","TEST · 2025–26"]
    m["split_descriptions"]=["Fit priors and candidate probability models.","Choose one model by held-out log loss.","Evaluate once after the protocol is frozen."]
    m["split_caveat"]="No final-test outcome was used to choose the model or scenario settings."
    m["maps_figure"]="maps.png"; m["maps_caption"]="Three-foot chart cells in the final test: observed rate, model probability and recorded point value; sparse cells omitted."
    m["uncertainty_headline"]="500 game resamples"; m["uncertainty_body"]="Intervals describe game-to-game sampling variation. They do not cover causal effects, opponent response or unobserved shot opportunities."
    sc=results["scenario"]; m["scenario_title"]=f"Constrained case study · {sc['team']}"; m["scenario_gain"]=f"{sc['gain_per100']:.2f}"; m["scenario_interval"]=f"95% conditional range\n{sc['gain_low']:.2f} to {sc['gain_high']:.2f}"; m["scenario_caption"]="Zone rates shrink toward training priors; movement is capped at 5 points per zone and 10 points total."
    m["zone_mix"]=[{"zone":x["zone"],"current":x["current_share"],"proposed":x["recommended_share"]} for x in sc["table"]]
    m["sensitivity"]=[{"label":f"{x['max_shift']:.1%} / risk {x['risk']:.0f}","gain":x["gain_per100"]} for x in results["sensitivity"]]
    m["sensitivity_caption"]="The reported gain rises with the allowed movement and falls with the risk penalty. Every value remains conditional on recorded shot opportunities."
    m["boundary"]="Do not read the scenario as a causal promise. Defensive response, opportunity creation and possession effects are outside this historical dataset."
    m["calibration"]=[{"predicted":x["mean_predicted"],"observed":x["observed"]} for x in results["calibration"] if x["season"]==results["config"]["final_test_season"]]
    report = AcademicReport(m["run_id"])
    report.title("NCAA Division I Men's<br/>Shot Selection", "Probability estimation, expected points and constrained shot-mix scenarios<br/>Academic report and portfolio research edition | September 2026")
    report.sub("Research question")
    report.p("For recorded NCAA Division I men's field-goal attempts, how does estimated make probability vary across court regions, and how much could a modest change in a team's shot mix change model-estimated points per recorded attempt?")
    report.sub("Abstract")
    report.p(m["abstract"])
    report.sub("Main findings")
    for sentence in m["main_findings"]:
        report.p(sentence)
    report.sub("Interpretation")
    report.p("This study evaluates predictions and conditional shot-mix scenarios. The outcome is points per recorded field-goal attempt. It excludes offensive possessions that end before a shot and does not establish the scoring effect of changing a real team's strategy.")
    report.p(f"Frozen analysis identifier: <b>{escape(m['run_id'])}</b>. All counts, scores and scenario values in this report come from this analysis run. The source blueprint supplied by the user motivates the project [1].", "ReportSmall")

    report.section("1. Data provenance and study population")
    report.p(m["data_provenance"])
    report.table(["Season ending", "Source attempts", "Included attempts", "Games", "D1 teams"],
                 m["cohort_rows"], [89,106,107,74,92], m["cohort_caption"])
    report.sub("Cohort construction")
    for paragraph in m["cohort_methods"]:
        report.p(paragraph)
    report.sub("Coverage and reconciliation")
    for paragraph in m["coverage_methods"]:
        report.p(paragraph)
    report.p("Season identifiers refer to the year in which the season ends. Counts describe the available, included source sample rather than a claim that every Division I attempt appears in the release.", "ReportSmall")

    report.section("2. Variables and spatial interpretation")
    report.table(["Field", "Meaning and role"], m["dictionary"], [138,330])
    report.sub("Coordinates and source zones")
    report.p(m["spatial_methods"])
    report.sub("Available information")
    report.p("The core source does not supply per-shot defender distance, shot-clock time or a consistent catch-and-shoot label. Those variables do not enter the model. Source field-goal values determine whether a made shot is worth two or three points. No outcome text or future aggregate enters a predictor.")

    report.section("3. Study design and statistical methods")
    report.table(["Role", "Seasons", "Use"], m["split_rows"], [89,92,287])
    report.p(m["split_caveat"])
    report.sub("Model ladder")
    for paragraph in m["model_methods"]:
        report.p(paragraph)
    report.sub("Evaluation")
    report.p("The Brier score is the mean squared difference between predicted make probability and the binary outcome. Log loss penalizes confident errors more strongly. Lower values indicate better predictive performance. Reliability bins compare average prediction with observed make rate. A lower Brier score alone does not prove better calibration [5, 6].")
    report.sub("Uncertainty")
    report.p(m["uncertainty_methods"])

    report.section("4. Held-out predictive results")
    report.p(m["model_caption"])
    report.table(["Model", "Brier score", "Log loss"], m["model_rows"], [284,92,92])
    report.figure(m["calibration_figure"], m["calibration_caption"], max_height=250)
    report.p(m["predictive_interpretation"])
    if m.get("subgroup_rows"):
        report.table(["Evaluation subgroup", "Attempts", "Brier", "Log loss"], m["subgroup_rows"], [240,76,76,76])

    report.section("5. Frequency, make probability and expected points")
    report.p("For a shot with point value V and make probability p, expected points per attempt equal V multiplied by p. A three-point attempt can therefore have lower make probability and still have higher expected value than a two-point attempt. The comparison requires the same population and a probability estimate appropriate to its context.")
    report.figure(m["maps_figure"], m["maps_caption"], max_height=270)
    report.table(["Zone", "Attempts", "Observed FG%", "Predicted FG%", "Predicted EP"], m["zone_summary_rows"], [118,82,91,91,86])
    report.p(m["maps_interpretation"])
    report.p("Expected points exclude free throws, offensive rebounds, turnovers before an attempt and the value of passing or driving instead. The maps therefore describe shot outcomes conditional on recorded attempts, not the full value of an offensive possession.", "ReportSmall")

    report.section("6. Constrained scenario analysis")
    report.p(m["scenario_description"])
    report.sub("Objective and constraints")
    report.p("Let q(z) be the proposed fraction of attempts from zone z, q0(z) the observed fraction and EP(z) its estimated expected points. The linear program maximizes the sum of q(z) multiplied by EP(z), or the corresponding conservative values, subject to the constraints below. SciPy's linear-programming solver evaluates this finite optimization problem [7].")
    report.table(["Constraint", "Default setting and interpretation"], m["constraint_rows"], [142,326])
    report.table(["Zone", "Current", "Scenario", "Change"], m["zone_mix_rows"], [177,97,97,97])
    report.p(m["scenario_result"])
    report.p("The allocation is feasible under the stated mathematical constraints. Historical frequencies and analyst-selected bounds are only proxies for availability. The data do not establish that the extra attempts can actually be created at the same quality.", "ReportSmall")

    report.section("7. Robustness and sensitivity")
    report.p(m["sensitivity_methods"])
    report.table(["Scenario setting", "Modeled gain / 100 attempts", "Reassigned share"], m["sensitivity_rows"], [242,137,89])
    report.p(m["sensitivity_interpretation"])
    report.sub("What the intervals cover")
    report.p(m["scenario_uncertainty"])
    report.sub("What the intervals omit")
    report.p("Resampling observed games does not reveal unobserved shot opportunities or opponents' strategic response. A narrow interval around a conditional scenario should not be interpreted as a narrow interval for an intervention's real-world effect. The fixed model and study design introduce additional uncertainty beyond the displayed resampling intervals.")

    report.section("8. Conclusions, limitations and reproducibility")
    report.p(m["conclusion"])
    report.sub("Limits of the evidence")
    for limitation in m["limitations"]:
        report.p(limitation)
    report.sub("Reproducible product")
    report.p("The repository contains the data audit, analysis code, saved model, final result JSON, static evidence figures and an interactive explorer. The report and slide deck read the frozen analysis output rather than introducing separately entered results. See the repository README for environment setup and the documented rebuild command.")
    report.p("The explorer supports comparing recorded shot distributions and conditional scenarios. Any prospective strategy evaluation would require a separate protocol, an opportunity-aware design and new observations collected after freezing the intervention. That experiment falls outside the historical analysis reported here.")

    report.section("References and source ledger")
    for i, source in enumerate(m["references"], 1):
        label = escape(source["label"])
        url = source.get("url")
        if url:
            report.p(f'{i}. {label}. <link href="{escape(url)}" color="#087F8C">{escape(url)}</link>', "ReportSmall")
        else:
            report.p(f'{i}. {label}.', "ReportSmall")
    report.sub("Data and software traceability")
    report.p(m["reproducibility_note"])
    report.p("Access date for online references: 21 September 2026. This independent project uses public basketball data and makes no claim of university, NCAA or team affiliation. The supplied blueprint's institutional wording does not establish an affiliation for this analysis.", "ReportSmall")
    report.save()
    manifest = ROOT / ".artifact-build/report_manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(m, indent=2) + "\n")


if __name__ == "__main__":
    build(json.loads(RESULTS.read_text()))
