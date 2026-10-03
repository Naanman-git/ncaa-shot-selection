"""Check the actual downloadable documents, their original sources and public routes."""
from io import BytesIO
import json
from pathlib import Path
import re
import shutil

from pypdf import PdfReader
import pytest
from streamlit.testing.v1 import AppTest

from ncaa_shot_selection.research_downloads import DOWNLOADS, research_pdf, source_download

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("item", DOWNLOADS, ids=lambda item: item.key)
def test_pdf_embeds_exact_original_and_accessible_source_link(item):
    reader = PdfReader(BytesIO(research_pdf(ROOT, item)))
    assert reader.attachments[item.source_name] == [(ROOT / item.source_path).read_bytes()]
    assert reader.metadata["/SourceURL"] == item.source_url
    links = [str(annotation.get_object().get("/A", {}).get("/URI", ""))
             for page in reader.pages for annotation in page.get("/Annots", [])]
    assert item.source_url in links
    text = "\n".join(page.extract_text() for page in reader.pages)
    normalized = re.sub(r"\s+", " ", text)
    assert "No GitHub account is needed" in text
    assert "Attachments panel" in normalized
    if item.key == "analysis-json":
        results = json.loads((ROOT / item.source_path).read_text())
        assert "Complete JSON appendix" in text
        assert all(f'"{key}"' in text for key in results)
        assert "legacy 2023-25 exploratory cleaning metadata" in text
        final = next(row for row in results["model_comparison"]
                     if row["season"] == results["config"]["final_test_season"]
                     and row["model"] == results["selected_model"])
        assert f"Mean Brier score: {final['brier']:.4f}" in text
        assert f"Mean log loss: {final['log_loss']:.4f}" in text
    else:
        normalized = re.sub(r"\s+", " ", text)
        # Each paragraph, list item and heading from the original survives conversion.
        for block in (ROOT / item.source_path).read_text().split("\n\n"):
            if block.startswith("```"):
                block = block.removeprefix("```bash\n").removesuffix("\n```")
            block = re.sub(r"(?m)^#{1,3} ", "", block).replace("`", "")
            assert re.sub(r"\s+", " ", block.strip()) in normalized


@pytest.mark.parametrize("item", DOWNLOADS, ids=lambda item: item.key)
def test_original_source_link_opens_correct_download_without_loading_shots(item):
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10)
    app.query_params["source"] = item.key
    app.run()
    assert not app.exception
    buttons = app.get("download_button")
    assert len(buttons) == 1
    assert "Download original" in buttons[0].proto.label
    assert item.title in app.title[0].value
    assert not app.selectbox  # The source page does not build the full explorer.
    assert "loading" not in " ".join(element.value.lower() for element in app.info)


def test_unrecognized_source_cannot_read_arbitrary_files():
    assert source_download("../../.env") is None
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10)
    app.query_params["source"] = "../../.env"
    app.run()
    assert not app.exception
    assert app.title[0].value == "Research download not found"
    assert not app.get("download_button")


def test_pdf_integrity_rejects_changed_source_and_changed_document(tmp_path):
    item = DOWNLOADS[0]
    for path in [item.source_path, "output/pdf/research_downloads.json",
                 f"output/pdf/{item.pdf_name}"]:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, target)
    source = tmp_path / item.source_path
    original = source.read_bytes()
    source.write_bytes(original + b" ")
    with pytest.raises(ValueError, match="rebuilt"):
        research_pdf(tmp_path, item)
    source.write_bytes(original)
    pdf = tmp_path / "output/pdf" / item.pdf_name
    pdf.write_bytes(pdf.read_bytes() + b" ")
    with pytest.raises(ValueError, match="rebuilt"):
        research_pdf(tmp_path, item)
