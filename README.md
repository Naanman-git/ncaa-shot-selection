# NCAA Division I men’s shot selection

This finished project studies recorded NCAA Division I men’s field-goal attempts. It produces a reproducible probability model, a transparent constrained shot-mix scenario, an interactive Streamlit explorer, an academic PDF and an editable presentation.

The frozen protocol uses native SportsDataverse NCAA shot releases for 2023–2026. A game enters the analysis only when both teams are present and native field-goal and three-point counts reconcile to the matching ESPN team box score. Exact duplicate rows are retained because the native source has no event identifier. The native zone and 2/3-point value are geometry-inferred by the upstream adapter, so the report describes them as recorded, inferred fields rather than tracking truth.

The model trains on 2022–23 and 2023–24, selects on 2024–25 by log loss, and evaluates once on 2025–26. The selected model is spatial L2 logistic regression with distance splines, angle, zone and strictly prior-day player-zone history. The scenario engine is separate: zone rates shrink toward training priors, movement is limited to ±5 percentage points per zone and an L1 budget of 0.20, and uncertainty is estimated with game resampling. It is not a causal intervention estimate.

## Run the product in VS Code

Open `CourtSense.code-workspace` in VS Code. The project environment has been installed on this computer. Choose **CourtSense: Streamlit dashboard** in Run and Debug, then press **F5**. It uses `.venv/bin/python` explicitly, so a previously selected system Python cannot override it. Open the address printed in the terminal (usually `http://127.0.0.1:8501`). If that port is occupied, Streamlit chooses the next available port.

The launch configuration sets the `src` import path automatically. If you prefer the terminal, create and install the project environment first:

```bash
python3 scripts/setup.py
python3 scripts/launch.py
```

Setup finds Python 3.11–3.14 (tested here with 3.12), creates `.venv`, and installs the dependencies. It also works when macOS `python3` points to 3.9. In VS Code the equivalent first-time task is **CourtSense: setup**. For editor completion and terminal use, select `.venv/bin/python` through **Python: Select Interpreter**. Start with F5 or the launcher, rather than the plain Python file runner. Keep the server terminal running while using the browser; press Ctrl+C to stop it.

## Deploy to Streamlit Community Cloud

The error in the screenshot is a repository connection message, not an application exception. Community Cloud can deploy only from a GitHub repository that your Streamlit account can access. This project now includes the required root `requirements.txt`, `runtime.txt`, `.streamlit/config.toml`, and a compact dashboard snapshot under `data/app/`.

1. Connect your GitHub account to Streamlit Community Cloud and grant it access to the private `Naanman-git/ncaa-shot-selection` repository.
2. Choose **Deploy an app**, select `main`, and set the main file to `app.py`.
3. In Advanced settings select Python 3.12, matching the tested local environment, then deploy. The Python selector is authoritative; do not rely on `runtime.txt` to configure Community Cloud.

Do not upload `data/raw/`, `.research-deps/`, or the large local build artifacts under `data/processed/` and `data/outputs/`; they are excluded from the deployment package. If you regenerate the analysis, run `PYTHONPATH=src .venv/bin/python scripts/prepare_deployment.py` and commit the updated `data/app/` snapshot. Streamlit’s deployment environment reads dependencies from the root `requirements.txt` and copies files that are present in the repository.

Primary evidence is in `data/outputs/final_results.json` and `data/processed/shots_scored.parquet`. Finished artifacts are [the academic report](output/pdf/ncaa_shot_selection_report.pdf) and [the editable presentation](output/presentation/ncaa_shot_selection.pptx). Raw files and source hashes are under `data/raw/` and `research/`.

The analysis predicts makes for recorded attempts and estimates conditional points per recorded attempt; it does not model all possessions, free throws, defensive response, shot availability or the causal effect of changing strategy. Public access and code do not grant permission to redistribute upstream data.
