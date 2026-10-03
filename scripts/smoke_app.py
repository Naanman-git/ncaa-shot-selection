"""Exercise the new pages using the tracked deployment snapshot."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()

def check():
    assert not app.exception, [e.message for e in app.exception]

check()
download_labels = {element.proto.label for element in app.get('download_button')}
assert {'Download selected team context', 'Download the complete guide'} <= download_labels
assert {'Download analysis results (PDF)', 'Download validation protocol (PDF)',
        'Download research report', 'Download presentation'} <= download_labels
app.button(key='check_stability').click().run();check()
app.text_input(key='guide_search').set_value('possessions').run();check()
assert any('Team context uses' in element.value for element in app.markdown)
app.text_input(key='guide_search').set_value('brier scroe').run();check()
assert any('0.2302' in element.value and 'full evaluation dataset' in element.value for element in app.markdown)
app.selectbox(key='validation_season').set_value(2025).run();check()
assert any('0.2297' in element.value and 'full evaluation dataset' in element.value for element in app.markdown)
app.button(key='guide_clear').click().run();check()
app.button(key='guide_quick_fg').click().run();check()
assert app.text_input(key='guide_search').value == 'fg_pct'
assert any('makes per 100 attempts' in element.value for element in app.markdown)
app.text_input(key='guide_search').set_value('volcanic eruptions').run();check()
assert any('couldn’t find that term' in element.value for element in app.info)
app.button(key='guide_suggestion_tour').click().run();check()
app.selectbox(key='season').set_value(2023).run();check()
app.selectbox(key='team').set_value('All Division I teams').run();check()
print('All pages, confidence diagnostics, glossary and season/team changes passed.')
