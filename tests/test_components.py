"""Unit tests for reflex-nivo: every chart renders, props map to nivo names."""

from __future__ import annotations

from typing import Any

import pytest
import reflex as rx
import reflex_nivo as nivo
from reflex_nivo.base import NivoComponent
from reflex_nivo.charts import __all__ as CHART_NAMES

CLASSES = [
    getattr(nivo, name)
    for name in CHART_NAMES
    if isinstance(getattr(nivo, name), type) and issubclass(getattr(nivo, name), NivoComponent)
]


class _State(rx.State):
    rows: list[dict[str, Any]] = []
    last: dict[str, Any] = {}

    @rx.event
    def clicked(self, datum: dict[str, Any]):
        self.last = datum


def _chart(container: rx.Component) -> rx.Component:
    return container.children[0]


def test_all_charts_are_exported():
    assert len(CLASSES) == 51
    for cls in CLASSES:
        assert cls.tag.startswith("Responsive")
        assert cls.library.startswith("@nivo/")
        assert cls.library.endswith(f"@{nivo.NIVO_VERSION}")


@pytest.mark.parametrize("cls", CLASSES, ids=lambda c: c.__name__)
def test_every_chart_renders(cls):
    kwargs = {"data": []} if "data" in cls.get_props() else {"features": []}
    container = cls.create(height="300px", **kwargs)
    rendered = str(container)
    assert cls.tag in rendered
    assert '["height"] : "300px"' in rendered
    assert "resolvedColorMode" in rendered  # default auto theme


def test_snake_case_props_become_camel_case():
    rendered = str(
        nivo.bar(
            data=_State.rows, index_by="country", enable_grid_x=True, axis_bottom=nivo.axis(legend_offset=32)
        )
    )
    assert "indexBy:" in rendered
    assert "enableGridX:true" in rendered
    assert '["legendOffset"] : 32' in rendered


def test_renamed_props():
    assert "id:" in str(_chart(nivo.pie(data=[], id_by="name")).render())
    rendered = str(nivo.calendar(data=[], from_date="2025-01-01", to_date="2025-12-31"))
    assert 'from:"2025-01-01T00:00:00"' in rendered
    assert 'to:"2025-12-31T00:00:00"' in rendered


def test_event_payload_is_sanitized():
    rendered = str(nivo.bar(data=[], on_click=_State.clicked))
    assert "reflexNivoSerialize(_datum)" in rendered
    assert "reflexNivoSerialize" in "".join(_chart(nivo.bar(data=[])).add_custom_code())


def test_container_props_and_typo_detection():
    container = nivo.line(data=[], width="50%", min_height="200px", class_name="x")
    assert "min-height" in str(container) or "minHeight" in str(container) or "min_height" in str(container)
    with pytest.raises(TypeError, match="enable_grid_x"):
        nivo.line(data=[], enable_gridx=True)


def test_explicit_theme_is_kept():
    rendered = str(nivo.pie(data=[], theme=nivo.themes.DARK))
    assert "resolvedColorMode" not in rendered


def test_default_props_workaround():
    rendered = str(nivo.geo_map_canvas(features=[]))
    assert '"graticule"' in rendered and '"features"' in rendered


def test_helpers():
    assert nivo.props(tick_size=5, tick_rotation=None) == {"tickSize": 5}
    assert nivo.margin(1, 2, 3, 4) == {"top": 1, "right": 2, "bottom": 3, "left": 4}
    assert nivo.inherit("color", ("darker", 1.6)) == {"from": "color", "modifiers": [["darker", 1.6]]}
    assert nivo.scale("linear", min="auto", stacked=True) == {
        "type": "linear",
        "min": "auto",
        "stacked": True,
    }
    assert nivo.legend(data_from="keys")["dataFrom"] == "keys"
    assert nivo.pattern_lines_def("l", line_width=3)["lineWidth"] == 3
    assert nivo.fill_rule("dots", {"id": "a"}) == {"match": {"id": "a"}, "id": "dots"}
    assert str(nivo.js("v => v * 2")) == "(v => v * 2)"
    assert "reflexNivoTemplate" in str(nivo.template("{id}"))
    assert "reflexNivoTooltip" in str(nivo.tooltip("<b>{id}</b>", style={"font_size": 12}))
    assert '["fontSize"] : 12' in str(nivo.tooltip("x", style={"font_size": 12}))


def test_theme_merge():
    merged = nivo.themes.merge(nivo.themes.LIGHT, {"text": {"fontSize": 20}})
    assert merged["text"]["fontSize"] == 20
    assert merged["text"]["fill"] == nivo.themes.LIGHT["text"]["fill"]
    assert nivo.themes.LIGHT["text"]["fontSize"] == 11
