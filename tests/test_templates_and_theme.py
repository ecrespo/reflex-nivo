"""The injected JavaScript must stay small and predictable on a busy page."""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest
import reflex_nivo as nivo
from reflex_nivo.base import NivoComponent


def _js(chart) -> str:
    return "".join(NivoComponent.add_custom_code(chart.children[0]))


def _run_node(script: str) -> dict:
    result = subprocess.run(
        [shutil.which("node"), "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_the_auto_theme_is_not_inlined_into_every_chart():
    """Ten charts used to carry ten copies of the full light+dark theme."""
    rendered = str(nivo.bar(data=[]))
    # A marker that only appears inside the theme literal itself.
    assert rendered.count("outlineOpacity") == 0, "the theme literal is inlined in the chart props"


def test_the_auto_theme_literal_is_injected_once_per_page():
    assert "outlineOpacity" in _js(nivo.bar(data=[]))


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_an_unserializable_value_interpolates_as_empty_text():
    """`JSON.stringify(undefined)` is undefined, which used to print as text."""
    out = _run_node(
        _js(nivo.bar(data=[]))
        + """
        const source = {ok: "x"};
        source.dom = {nativeEvent: {}, currentTarget: {}};
        console.log(JSON.stringify({
            rendered: reflexNivoTemplate("[{ok}][{dom}][{missing}]")(source),
        }));
        """
    )
    assert out["rendered"] == "[x][][]"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_template_cache_is_bounded():
    """A template driven by state changes every render; the Map must not grow."""
    out = _run_node(
        _js(nivo.bar(data=[]))
        + """
        for (let i = 0; i < 5000; i++) reflexNivoTemplate("value " + i + ": {id}");
        console.log(JSON.stringify({size: reflexNivoTemplateCache.size}));
        """
    )
    assert out["size"] <= 512
