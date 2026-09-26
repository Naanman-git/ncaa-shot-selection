# Data layout

`raw/` contains downloaded source files and is intentionally kept separate from derived tables.

The primary source is the SportsDataverse NCAA-native shot release:

`https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/ncaa_mbb_shots`

The downloaded files are listed with SHA-256 hashes in `../research/source_manifest.json` after the audit step. Do not edit raw files.

`templates/prospective_shots_template.csv` is a separate anonymous collection template for a future post-freeze validation experiment. It must never contain player names, contact information, or consent records. Its fields are defined in `../docs/CODING_GUIDE.md`.

For the dashboard, `processed/shots_scored.parquet` and
`outputs/final_results.json` are the portable evidence snapshot. They are
deliberately kept in the repository so a clean Streamlit checkout can open the
explorer without downloading private or untracked source files. The raw NCAA
and ESPN downloads, full rebuild intermediates, and fitted binary are ignored
by Git. Recreate them locally with the pipeline documented in the root
README.
