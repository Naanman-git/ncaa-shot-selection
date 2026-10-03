"""User-facing search, contextual accuracy and actual export coverage."""
from dataclasses import replace
from pathlib import Path
import ast
import csv
import json

import pyarrow.parquet as pq
import pytest

from ncaa_shot_selection.guide import GuideContext, guide_markdown, normalize, search_topics, selection_example
from ncaa_shot_selection.guide_catalog import BY_KEY, TOPICS

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("query, expected", [
    ("What does fg_pct mean?", "fg"), ("FG%", "fg"),
    ("points per shot", "observed-pps"), ("EXPECTED_PPS", "predicted-pps"),
    ("brier scroe", "brier"), ("make probablity", "probability"),
    ("what is log-loss?", "log-loss"), ("how accurate is this model?", "validation"),
    ("What does TO mean?", "turnovers"), ("FT", "ft"), ("OR", "rebounds"),
    ("pp", "pp"), ("mean", "weighted"), ("points per possession", "possession-rate"),
    ("95% confidence interval", "interval"), ("ρ", "hypothesis"),
])
def test_search_answers_real_terms_questions_and_typos(query, expected):
    assert search_topics(query)[0].key == expected


def test_unknown_query_does_not_invent_a_response():
    assert search_topics("volcanic eruptions") == []
    assert search_topics("   ") == []


def context():
    return GuideContext("Team A", 2026,
        {"count": 200, "games": 10, "fg_pct": .45, "observed_pps": 1.10, "expected_pps": 1.02},
        evaluation={"season": 2025, "model": "Spatial + player history", "n": 599333, "brier": .2297, "log_loss": .6518},
        team_label="Team A", team_totals={"games": 10, "possessions": 700, "points": 750, "free_throws": 100, "turnovers": 90},
        profile_label="Player B · Team A", profile_summary={"count": 80, "games": 8})


def test_selected_team_numbers_update_and_preserve_units():
    first = selection_example("fg", context())
    second = selection_example("fg", replace(context(), label="Player C", summary={"count": 10, "games": 2, "fg_pct": .30}))
    assert "45.0%" in first and "45.0 makes per 100" in first
    assert "Player C" in second and "30.0%" in second and "45.0%" not in second
    assert "110.0 actual field-goal points per 100" in selection_example("observed-pps", context())


def test_validation_context_uses_independent_evaluation_season():
    for key in ("brier", "log-loss"):
        answer = selection_example(key, context())
        assert "2024–25 full evaluation dataset" in answer and "599,333" in answer
        assert "Team A" not in answer and "sidebar team and player do not change" in answer
    changed = replace(context(), evaluation={"season": 2026, "model": "Spatial + player history", "n": 614611, "brier": .2302, "log_loss": .6528})
    assert "0.2302" in selection_example("brier", changed)
    assert "0.6528" in selection_example("log-loss", changed)


def test_context_and_player_examples_use_their_own_page_selection():
    c = replace(context(), label="Sidebar player")
    answer = selection_example("possession-rate", c)
    assert "Team A" in answer and "Sidebar player" not in answer and "1.071" in answer
    assert "Player B" in selection_example("trend", c)
    assert "Sidebar player" not in selection_example("trend", c)


def test_unavailable_and_feasible_scenarios_are_explained_honestly():
    assert "unavailable" in selection_example("gain", context())
    infeasible = replace(context(), scenario={"feasible": False, "message": "Cap conflicts with movement."})
    assert "No valid scoring gain" in selection_example("gain", infeasible)
    feasible = replace(context(), scenario={"feasible": True, "current_ep": 1, "recommended_ep": 1.03, "gain_per100": 3, "gain_low": -1, "gain_high": 4})
    answer = selection_example("gain", feasible)
    assert "+3.0 points per 100" in answer
    assert "-1.0 to +4.0" in answer and "unchanged zone efficiencies" in answer


def test_catalog_links_and_offline_download_are_complete():
    assert len(BY_KEY) == len(TOPICS)
    text = guide_markdown()
    assert (ROOT / "docs/BEGINNER_GUIDE.md").read_text() == text
    for entry in TOPICS:
        assert entry.meaning and entry.example and entry.details
        assert f"### {entry.title}" in text and entry.details in text
        assert all(key in BY_KEY for key in entry.related)


def test_actual_download_fields_and_displayed_table_labels_have_definitions():
    """Fail when an app export acquires a field the guide has not explained."""
    fields = set()
    def collect(value):
        if isinstance(value, dict):
            fields.update(value)
            for item in value.values():
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)
    collect(json.loads((ROOT / "data/app/final_results.json").read_text()))
    for name in ("shots_scored", "team_context"):
        fields.update(pq.read_schema(ROOT / f"data/app/{name}.parquet").names)
    with (ROOT / "data/templates/prospective_shots_template.csv").open() as stream:
        fields.update(next(csv.reader(stream)))
    tree = ast.parse((ROOT / "app.py").read_text())
    for call in ast.walk(tree):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr in {"NumberColumn", "CheckboxColumn"}:
            if call.args and isinstance(call.args[0], ast.Constant):
                fields.add(call.args[0].value)
    aliases = {normalize(alias) for entry in TOPICS for alias in (entry.title, *entry.aliases)}
    assert not {name for name in fields if normalize(name) not in aliases}
