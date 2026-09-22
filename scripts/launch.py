"""Launch the local explorer with a predictable interpreter and module path.

The dashboard should be started from the repository root. This helper keeps
that detail out of VS Code tasks and gives a useful install message when the
selected interpreter does not contain Streamlit.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def _module_available(python: str, environment: dict[str, str]) -> bool:
    probe = subprocess.run(
        [python, "-c", "import streamlit"],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return probe.returncode == 0


def _choose_python(environment: dict[str, str]) -> str:
    configured = environment.get("COURTSENSE_PYTHON")
    candidates = [Path(configured)] if configured else []
    candidates.extend(
        [
            ROOT / ".venv" / "bin" / "python",
            ROOT / ".venv" / "Scripts" / "python.exe",
            Path(sys.executable),
        ]
    )
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate:
            continue
        key = str(candidate)
        if key in seen or not candidate.exists():
            continue
        seen.add(key)
        if _module_available(key, environment):
            return key
    return str(Path(sys.executable))


def main() -> None:
    environment = os.environ.copy()
    search = [str(ROOT / "src")]
    if environment.get("PYTHONPATH"):
        search.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(search)
    python = _choose_python(environment)
    if not _module_available(python, environment):
        print("Streamlit is not installed in the selected Python interpreter.", file=sys.stderr)
        print("Create the project environment, then install requirements.txt:", file=sys.stderr)
        print("  python3 -m venv .venv", file=sys.stderr)
        print("  .venv/bin/python -m pip install -r requirements.txt", file=sys.stderr)
        print("You can override the interpreter with COURTSENSE_PYTHON=/path/to/python.", file=sys.stderr)
        raise SystemExit(2)
    # The bundled Codex runtime can identify Streamlit as a source checkout
    # and therefore enables its hidden development mode. In that mode an
    # explicit ``server.port`` flag is rejected; the normal wheel install in
    # .venv/ and on Community Cloud does not need this compatibility switch.
    environment.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")
    command = [
        python,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "app.py"),
        "--server.address=127.0.0.1",
        "--server.headless=true",
        *sys.argv[1:],
    ]
    try:
        raise SystemExit(subprocess.call(command, cwd=ROOT, env=environment))
    except KeyboardInterrupt:
        raise SystemExit(0)


if __name__ == "__main__":
    main()
