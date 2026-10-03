"""Stable public source links and integrity-checked, prebuilt research PDFs."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

APP_URL = "https://courtsense-ncaa.streamlit.app/"


@dataclass(frozen=True)
class ResearchDownload:
    key: str
    title: str
    source_path: str
    source_name: str
    source_mime: str
    pdf_name: str

    @property
    def source_url(self) -> str:
        return f"{APP_URL}?source={self.key}"


DOWNLOADS = (
    ResearchDownload(
        "analysis-json", "Analysis results", "data/app/final_results.json",
        "ncaa_analysis_results.json", "application/json", "ncaa_analysis_results.pdf",
    ),
    ResearchDownload(
        "validation-markdown", "Prospective validation protocol",
        "docs/PROSPECTIVE_VALIDATION_PROTOCOL.md", "PROSPECTIVE_VALIDATION_PROTOCOL.md",
        "text/markdown", "ncaa_validation_protocol.pdf",
    ),
)


def source_download(key: str) -> ResearchDownload | None:
    """Only named public research exports can be reached through query parameters."""
    return next((item for item in DOWNLOADS if item.key == key), None)


def research_pdf(root: Path, item: ResearchDownload) -> bytes:
    """Reject stale documents instead of serving a PDF from a different source."""
    manifest = json.loads((root / "output/pdf/research_downloads.json").read_text())
    entry = manifest[item.key]
    source = (root / item.source_path).read_bytes()
    pdf = (root / "output/pdf" / item.pdf_name).read_bytes()
    if (entry["source_sha256"] != hashlib.sha256(source).hexdigest()
            or entry["pdf_sha256"] != hashlib.sha256(pdf).hexdigest()):
        raise ValueError("Research PDFs need to be rebuilt for the current source files.")
    return pdf
