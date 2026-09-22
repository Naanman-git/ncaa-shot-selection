# Running and deploying CourtSense

The application is a Streamlit app. It is not a regular Python script, so VS Code must launch `streamlit run app.py` through the included `CourtSense: Streamlit dashboard` debug configuration.

Local setup:

1. Open `CourtSense.code-workspace` in VS Code.
2. On a fresh computer, run **CourtSense: setup** (already completed here).
3. Choose `.venv/bin/python` in the Command Palette: **Python: Select Interpreter**.
4. Start **CourtSense: Streamlit dashboard** from the Run and Debug panel.
5. Open the address printed in the terminal. The default is `http://localhost:8501`; an occupied port causes Streamlit to choose another. Keep the terminal running.

The application loads the compact tracked snapshot in `data/app/`. This keeps deployment independent of the large raw downloads. The snapshot is rebuilt after a local analysis run with:

```bash
PYTHONPATH=src .venv/bin/python scripts/prepare_deployment.py
```

The project is available in the private GitHub repository `Naanman-git/ncaa-shot-selection`. In Streamlit Community Cloud, connect the GitHub account and grant access to this repository, then deploy `app.py` from the `main` branch. The repository includes `requirements.txt`, `runtime.txt`, `.streamlit/config.toml`, `src/`, and `data/app/`. The Streamlit account must be authorized to access the private repository.

The yellow chart messages came from an older Streamlit installation receiving the newer chart-width argument. Streamlit is now pinned to the tested 1.64.0 version, and a compatibility helper passes only supported width arguments. For cloud deployment select Python 3.12 in Advanced settings.
