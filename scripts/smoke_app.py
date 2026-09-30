"""Exercise the new pages using the tracked deployment snapshot."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()

def check():
    assert not app.exception, [e.message for e in app.exception]

check()
for chapter in app.select_slider(key='story_chapter').options:
    app.select_slider(key='story_chapter').set_value(chapter).run();check()
app.button(key='check_stability').click().run();check()
app.text_input(key='guide_search').set_value('possessions').run();check()
app.selectbox(key='season').set_value(2023).run();check()
app.selectbox(key='team').set_value('All Division I teams').run();check()
print('All pages, story chapters, confidence diagnostics, glossary and season/team changes passed.')
