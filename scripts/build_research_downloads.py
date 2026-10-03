#!/usr/bin/env python3
"""Build readable research downloads, each with its exact original embedded.

Run after preparing data/app/. Requires scripts/requirements-pdf.txt; no PDF
generation libraries are needed by the deployed Streamlit application.
"""
from __future__ import annotations

import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import sys
import textwrap
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageBreak, PageTemplate,
    Paragraph, Preformatted, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ncaa_shot_selection.research_downloads import DOWNLOADS, ResearchDownload

NAVY = colors.HexColor("#172B3A")
TEAL = colors.HexColor("#167D8D")
MUTED = colors.HexColor("#596C75")
CREAM = colors.HexColor("#FCFAF5")
LINE = colors.HexColor("#D8DEDB")
WIDTH = 492


def plain(text: str) -> str:
    return str(text).replace("\u2013", "-").replace("\u2014", "-").replace("\u2011", "-")


def season(year: int) -> str:
    return f"{year - 1}-{str(year)[-2:]}"


class Document:
    def __init__(self, item: ResearchDownload):
        self.item = item
        self.flow = []
        self.styles = getSampleStyleSheet()
        for name, options in {
            "TitleCS": dict(fontName="Helvetica-Bold", fontSize=28, leading=32, spaceAfter=14),
            "SubtitleCS": dict(fontSize=11, leading=16, textColor=MUTED, spaceAfter=15),
            "HeadingCS": dict(fontName="Helvetica-Bold", fontSize=16, leading=20, spaceBefore=12, spaceAfter=9, keepWithNext=True),
            "SubCS": dict(fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=TEAL, spaceBefore=9, spaceAfter=6, keepWithNext=True),
            "BodyCS": dict(fontSize=10, leading=14.5, spaceAfter=8),
            "SmallCS": dict(fontSize=8.6, leading=12.5, textColor=MUTED, spaceAfter=7),
            "CellCS": dict(fontSize=8.5, leading=11.5),
            "CodeCS": dict(fontName="Courier", fontSize=7.4, leading=10),
        }.items():
            self.styles.add(ParagraphStyle(name, fontName="Helvetica", textColor=NAVY,
                                           alignment=TA_LEFT, **{k:v for k,v in options.items()
                                                               if k not in ("fontName", "textColor")}))
            self.styles[name].fontName = options.get("fontName", "Helvetica")
            self.styles[name].textColor = options.get("textColor", NAVY)

    def p(self, text, style="BodyCS"):
        self.flow.append(Paragraph(plain(text), self.styles[style]))

    def section(self, title, *, page=False):
        if page:
            self.flow.append(PageBreak())
        self.p(escape(title), "HeadingCS")

    def table(self, headers, rows, widths):
        header = ParagraphStyle("HeaderCS", parent=self.styles["CellCS"],
                                fontName="Helvetica-Bold", textColor=colors.white)
        cells = [[Paragraph(escape(plain(v)), header if n == 0 else self.styles["CellCS"])
                  for v in row] for n, row in enumerate([headers, *rows])]
        table = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), NAVY), ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CREAM]),
            ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LINEBELOW", (0,-1), (-1,-1), .6, LINE),
        ]))
        self.flow.extend([table, Spacer(1, 10)])

    def original(self, source: bytes):
        self.p("Your original file is included", "SubCS")
        self.p(f'<a href="{self.item.source_url}" color="#167D8D"><b>Download the original '
               f'{"JSON" if self.item.key == "analysis-json" else "Markdown (.md)"} file from CourtSense</b></a>')
        self.p(f"The link opens a CourtSense page with a download button. No GitHub account is needed. "
               f"This PDF also embeds <b>{escape(self.item.source_name)}</b>, unchanged. "
               "In a PDF reader that supports attachments, open the Attachments panel to save it. "
               "If your browser hides attachments, use the link above.", "SmallCS")
        self.p("The web link serves the app's current source file. The attachment preserves the exact "
               "version used to create this PDF, even if the app is updated later.", "SmallCS")

    def build(self, source: bytes) -> bytes:
        buffer = BytesIO()
        item = self.item

        def decorate(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(TEAL)
            canvas.drawString(60, 756, "COURTSENSE / RESEARCH DOWNLOADS")
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(552, 756, "NCAA DIVISION I MEN")
            canvas.setStrokeColor(LINE)
            canvas.line(60, 48, 552, 48)
            canvas.setFont("Helvetica", 7)
            canvas.drawString(60, 34, item.title)
            canvas.drawRightString(552, 34, f"Page {doc.page}")
            canvas.restoreState()

        doc = BaseDocTemplate(buffer, pagesize=(612,792), leftMargin=60, rightMargin=60,
                              topMargin=62, bottomMargin=62, title=f"CourtSense - {item.title}",
                              author="CourtSense NCAA Shot Selection Project")
        doc.addPageTemplates(PageTemplate(id="research", frames=[Frame(60,62,WIDTH,668,
                              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                              onPage=decorate))
        doc.build(self.flow)
        writer = PdfWriter(clone_from=PdfReader(buffer))
        attachment = writer.add_attachment(item.source_name, source)
        attachment.description = TextStringObject("Exact original source used to generate this PDF")
        attachment.subtype = NameObject(f"/{item.source_mime}")
        writer.root_object[NameObject("/PageMode")] = NameObject("/UseAttachments")
        writer.add_metadata({"/SourceSHA256": hashlib.sha256(source).hexdigest(),
                             "/SourceURL": item.source_url})
        output = BytesIO()
        writer.write(output)
        return output.getvalue()


def analysis_document(item: ResearchDownload, source: bytes) -> Document:
    d = json.loads(source)
    doc = Document(item)
    doc.p("Analysis results", "TitleCS")
    doc.p("A readable view of the frozen NCAA shot-selection analysis, with the full JSON "
          "included as an appendix and an original-file attachment.", "SubtitleCS")
    doc.original(source)
    doc.section("What this download represents")
    total = sum(x["attempts"] for x in d["season_summary"])
    doc.p(f"This saved build contains <b>{total:,} recorded field-goal attempts</b> across four seasons. "
          "It describes the full analysis cohort and a saved Ohio State case study. "
          "It does not change when you select another team, player or scenario in the app.")
    doc.p(f"<b>Analysis run:</b> {escape(d['run_id'])}<br/>"
          f"<b>Source generated:</b> {escape(d['generated_utc'])}<br/>"
          f"<b>Selected model:</b> {escape(d['selected_model'])}", "SmallCS")
    doc.table(["Season", "Role", "Attempts", "Games", "Teams"], [
        [season(x["season"]), "Training" if x["season"] in d["config"]["training_seasons"] else
         "Model selection" if x["season"] == d["config"]["selection_season"] else "Final evaluation",
         f'{x["attempts"]:,}', f'{x["games"]:,}', str(x["teams"])] for x in d["season_summary"]
    ], [86,138,99,85,84])
    doc.p("Included games are reconciled with team box scores. This is an eligible, recorded "
          "sample, not a claim of complete NCAA coverage. Counts above come from season_summary.", "SmallCS")

    doc.section("Model validation: two separate error scores", page=True)
    doc.p("These scores test how predicted make probabilities agreed with outcomes in later games. "
          "Lower is better for each score. Neither score is a shooting percentage.")
    for metric, title, definition in [
        ("brier", "Mean Brier score", "The average squared difference between the predicted chance and "
         "the made-or-missed result. A prediction of 0.70 on a made shot has error (0.70 - 1)^2 = 0.09. "
         "Perfect predictions score 0."),
        ("log_loss", "Mean log loss", "The average negative natural logarithm of the probability assigned "
         "to the result that occurred. Confident wrong predictions receive especially large penalties. "
         "Perfect predictions score 0; compare models on the same shots."),
    ]:
        final = next(x for x in d["model_comparison"] if x["model"] == d["selected_model"]
                     and x["season"] == d["config"]["final_test_season"])
        ci = d["test_confidence_intervals"][metric]
        doc.p(f"{title}: {final[metric]:.4f}", "SubCS")
        doc.p(definition)
        doc.p(f"Selected model, {season(final['season'])}; {final['n']:,} attempts. "
              f"95% game-bootstrap interval: {ci['low']:.4f} to {ci['high']:.4f}.", "SmallCS")
    doc.table(["Season", "Model", "Attempts", "Brier", "Log loss"], [
        [season(x["season"]), x["model"], f'{x["n"]:,}', f'{x["brier"]:.4f}',
         f'{x["log_loss"]:.4f}'] for x in d["model_comparison"]
    ], [68,200,84,70,70])
    doc.p("Training transformations use 2022-23 and 2023-24. The 2024-25 selection minimizes "
          "log loss; 2025-26 evaluates the fixed model. Player histories update only from earlier "
          "dates in the same season. Calibration bins and full-precision scores are in the appendix.", "SmallCS")

    doc.section("Saved scenario and interpretation", page=True)
    sc = d["scenario"]
    doc.p(f"<b>{escape(sc['team'])}, {season(sc['season'])}</b>: {sc['attempts']:,} attempts "
          f"across {sc['games']:,} games. Estimated current points per attempt: {sc['current_ep']:.3f}; "
          f"scenario: {sc['recommended_ep']:.3f}.")
    doc.p(f"Conditional estimated change: <b>{sc['gain_per100']:+.2f} points per 100 attempts</b>, "
          f"with a 95% game-bootstrap interval of {sc['gain_low']:+.2f} to {sc['gain_high']:+.2f}. "
          "This assumes zone efficiencies persist after changing the mix. It does not establish "
          "that a coaching change would improve game outcomes.")
    names = {"rim":"At the rim", "paint":"Paint distance band", "mid":"Mid-range", "corner3":"Corner three", "abovebreak3":"Above-break three"}
    doc.table(["Zone", "Attempts", "Current share", "Scenario share", "Estimated pts / attempt"], [
        [names[x["zone"]], f'{x["count"]:,}', f'{x["current_share"]:.1%}',
         f'{x["recommended_share"]:.1%}', f'{x["ep"]:.3f}'] for x in sc["table"]
    ], [126,66,92,92,116])
    doc.p("Key limitations", "SubCS")
    for limitation in d["limitations"]:
        doc.p(escape(limitation), "SmallCS")

    doc.section("Complete JSON appendix", page=True)
    doc.p("Every field and full-precision value from the original analysis JSON appears below. "
          "Long lines wrap for the printed page. Use the embedded JSON or the link on page 1 "
          "for a file that Python or a text editor can read directly.")
    doc.p("<b>Audit context:</b> audit contains legacy 2023-25 exploratory cleaning metadata, "
          "including a duplicate-removal policy. It is preserved unchanged for transparency. "
          "It is not the count or cleaning policy of the final reconciled 2023-26 cohort; "
          "use season_summary and the research report for that cohort.", "SmallCS")
    # ASCII JSON avoids unsupported glyphs while preserving all keys and values.
    encoded = json.dumps(d, indent=2, ensure_ascii=True)
    wrapped = []
    for line in encoded.splitlines():
        wrapped.extend(textwrap.wrap(line, width=104, expand_tabs=False,
                                    replace_whitespace=False, drop_whitespace=False,
                                    subsequent_indent="    ") or [""])
    doc.flow.append(Preformatted("\n".join(wrapped), doc.styles["CodeCS"]))
    return doc


def inline_markdown(text: str) -> str:
    return re.sub(r"`([^`]+)`", lambda match: f'<font name="Courier">{escape(match[1])}</font>', escape(text))


def protocol_document(item: ResearchDownload, source: bytes) -> Document:
    doc = Document(item)
    doc.p("Prospective validation protocol", "TitleCS")
    doc.p("The complete plan for collecting and evaluating new attempts after freezing the "
          "historical analysis. No real prospective experiment or new outcome is claimed.", "SubtitleCS")
    doc.original(source)
    # Preserve every original section, paragraph, list item and command.
    lines = source.decode("utf-8").splitlines()
    paragraph = []
    code = []
    in_code = False

    def flush():
        if paragraph:
            doc.p(inline_markdown(" ".join(paragraph)))
            paragraph.clear()

    for line in lines:
        if line.startswith("```"):
            flush()
            if in_code:
                doc.flow.extend([Preformatted("\n".join(code), doc.styles["CodeCS"]), Spacer(1,12)])
                code.clear()
            in_code = not in_code
        elif in_code:
            code.append(line)
        elif line.startswith("# "):
            continue  # The same title is already rendered above.
        elif line.startswith("## "):
            flush()
            doc.section(line[3:])
        elif line.startswith("### "):
            flush()
            doc.p(escape(line[4:]), "SubCS")
        elif not line.strip():
            flush()
        elif line.startswith("- ") or re.match(r"\d+\. ", line):
            flush()
            doc.p(inline_markdown(line))
        else:
            paragraph.append(line)
    flush()
    return doc


def main():
    output = ROOT / "output/pdf"
    output.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for item in DOWNLOADS:
        source = (ROOT / item.source_path).read_bytes()
        builder = analysis_document if item.key == "analysis-json" else protocol_document
        pdf = builder(item, source).build(source)
        (output / item.pdf_name).write_bytes(pdf)
        manifest[item.key] = {
            "source_path": item.source_path, "source_name": item.source_name,
            "source_url": item.source_url, "source_sha256": hashlib.sha256(source).hexdigest(),
            "pdf_name": item.pdf_name, "pdf_sha256": hashlib.sha256(pdf).hexdigest(),
        }
        print(f"Built {item.pdf_name}: {len(PdfReader(BytesIO(pdf)).pages)} pages; original embedded")
    (output / "research_downloads.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
