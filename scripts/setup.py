"""Create the project environment using a supported Python (bootstrap works on 3.9)."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENV_PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def supported(executable):
    try:
        result = subprocess.run([str(executable), "-c",
            "import sys; sys.exit(0 if (3,11) <= sys.version_info[:2] < (3,15) else 1)"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return result.returncode == 0
    except OSError:
        return False


def main():
    if ENV_PYTHON.exists():
        if not supported(ENV_PYTHON):
            raise SystemExit("Existing .venv uses an unsupported Python. Rename .venv and run setup again.")
    else:
        candidates = [sys.executable]
        candidates += [shutil.which(name) for name in ["python3.12", "python3.11", "python3.13", "python3.14"]]
        # Optional desktop runtime; normal Python installations are tried first.
        candidates.append(str(Path.home()/".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"))
        python = next((p for p in candidates if p and supported(p)), None)
        if not python:
            raise SystemExit("Install Python 3.11 or newer from python.org, then rerun this setup.")
        print("Creating project environment with " + python, flush=True)
        subprocess.run([python, "-m", "venv", str(ROOT/".venv")], check=True)
    print("Installing project dependencies…", flush=True)
    subprocess.run([str(ENV_PYTHON), "-m", "pip", "install", "-r",
                    str(ROOT/"scripts/requirements-dev.txt")], cwd=ROOT, check=True)
    print("Ready. In VS Code select .venv/bin/python and press F5, or run: python3 scripts/launch.py")


if __name__ == "__main__":
    main()
