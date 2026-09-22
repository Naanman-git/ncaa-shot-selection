from __future__ import annotations

from ncaa_shot_selection.streamlit_compat import full_width_kwargs


def modern_element(value, *, width="stretch"):
    return value


def legacy_element(value, use_container_width=True, **kwargs):
    return value


def narrow_element(value):
    return value


def test_modern_streamlit_uses_width_stretch():
    assert full_width_kwargs(modern_element) == {"width": "stretch"}


def test_legacy_streamlit_uses_container_width_without_legacy_kwargs():
    assert full_width_kwargs(legacy_element) == {"use_container_width": True}


def test_unknown_signature_does_not_invent_keyword():
    assert full_width_kwargs(narrow_element) == {}
