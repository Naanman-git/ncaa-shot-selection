"""Small compatibility helpers for the Streamlit API transition.

Streamlit 1.50 exposes Plotly's legacy ``**kwargs`` while newer releases use
the explicit ``width`` parameter.  Passing ``width`` to the older signature
creates a visible deprecation warning even though the chart still renders.
Keeping the version check here makes the app work with either API without
pinning users to a particular Streamlit release.
"""
from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any


def full_width_kwargs(function: Callable[..., Any]) -> dict[str, Any]:
    """Return the supported keyword for a full-width Streamlit element.

    Streamlit 1.50 and earlier use ``use_container_width`` for Plotly charts;
    newer releases use ``width="stretch"``.  The same fallback is accepted by
    dataframes and download buttons, so the helper is useful for all three.
    """
    params = inspect.signature(function).parameters
    if "width" in params:
        return {"width": "stretch"}
    if "use_container_width" in params:
        return {"use_container_width": True}
    return {}
