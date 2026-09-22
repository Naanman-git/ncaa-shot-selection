from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ncaa_shot_selection import load_native_shots, prepare_shots


def main() -> None:
    raw = load_native_shots(ROOT / "data/raw")
    clean, report = prepare_shots(raw, ROOT)
    out = ROOT / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    clean.to_parquet(out / "shots_clean.parquet", index=False)
    (out / "cleaning_report.json").write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
