"""Unit tests for reflex-nivo: every chart renders, props map to nivo names."""

from __future__ import annotations

import json
import shutil
import subprocess
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
    def noop(self):
        pass

    @rx.event
    def clicked(self, datum: dict[str, Any]):
        self.last = datum


def _chart_js(declares: str) -> str:
    """The injected JavaScript block declaring `declares`."""
    blocks = NivoComponent.add_custom_code(nivo.sunburst(data=[]).children[0])
    return next(block for block in blocks if f"const {declares}" in block)


def _run_node(script: str) -> dict[str, Any]:
    """Run `script` under node and parse what it prints."""
    result = subprocess.run(
        [shutil.which("node"), "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


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


@pytest.mark.parametrize("shorthand", ["margin_x", "margin_y", "padding_x", "padding_y", "bg", "bg_color"])
def test_reflex_style_shorthands_reach_the_container(shorthand):
    # They are not CSS property names, so they must be allowed explicitly.
    assert nivo.pie(data=[], **{shorthand: "auto"}) is not None


def test_readme_sizing_example():
    assert nivo.pie(data=[], height="320px", max_width="600px", margin_x="auto") is not None


def test_explicit_none_hides_a_prop():
    # Reflex drops None props, so nivo would apply its own `axisBottom = {}`.
    rendered = str(nivo.bar(data=[], axis_bottom=None, axis_left=None))
    assert "axisBottom:null" in rendered
    assert "axisLeft:null" in rendered


def test_explicit_none_theme_means_nivos_own_theme():
    assert "theme:null" in str(nivo.pie(data=[], theme=None))
    assert "resolvedColorMode" in str(nivo.pie(data=[]))  # omitted -> auto


def test_events_nivo_does_not_declare_go_to_the_container():
    # @nivo/stream reads no onClick, so the handler must land on the <div>
    # instead of being swallowed by a component that ignores it.
    assert "on_click" not in nivo.Stream._nivo_event_names()
    container = nivo.stream(data=[], on_click=_State.noop)
    assert "onClick" in str(container)
    assert "onClick" not in str(_chart(container))


def test_nivo_events_still_reach_the_chart_with_the_datum():
    assert "on_click" in nivo.Bar._nivo_event_names()
    assert "reflexNivoSerialize" in str(_chart(nivo.bar(data=[], on_click=_State.clicked)))


def test_unknown_event_names_the_available_callbacks():
    with pytest.raises(TypeError, match="nivo callbacks on this chart: on_click"):
        nivo.sankey(data=[], on_arc_click=_State.clicked)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_serializer_keeps_hierarchy_datums_usable():
    """A drill-down datum must survive as valid `data=` for the chart."""
    out = _run_node(
        _chart_js("reflexNivoSerialize")
        + """
        const nest = (levels) => {
            let tree = {name: "leaf", loc: 1};
            for (let i = 0; i < levels; i++) tree = {name: "n" + i, children: [tree, {name: "x" + i}]};
            return tree;
        };
        console.log(JSON.stringify({
            typical: reflexNivoSerialize({data: nest(8)}),
            pathological: reflexNivoSerialize({data: nest(40)}),
        }));
        """
    )
    # A realistic drill-down datum survives whole, leaf included.
    assert "leaf" in json.dumps(out["typical"])
    # Deeper than the bound it degrades to an empty `children`, never to a null
    # child: d3-hierarchy cannot read one.
    assert "null" not in json.dumps(out["pathological"])
    deepest = out["pathological"]["data"]
    while deepest.get("children"):
        deepest = deepest["children"][0]
    assert deepest["children"] == []


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_serializer_keeps_shared_objects_and_shrinks_graphs():
    """A repeat is data, not a hole: only id-bearing ones shrink to the id."""
    out = _run_node(
        _chart_js("reflexNivoSerialize")
        + """
        const shared = {label: "X"};
        const identified = {id: "n1", label: "N"};
        const cyclic = {id: "c"};
        cyclic.parent = cyclic;
        console.log(JSON.stringify({
            shared: reflexNivoSerialize({a: shared, b: shared}),
            identified: reflexNivoSerialize({a: identified, b: identified}),
            cyclic: reflexNivoSerialize(cyclic),
        }));
        """
    )
    # Used to lose key "b" entirely when the object carried no id.
    assert out["shared"] == {"a": {"label": "X"}, "b": {"label": "X"}}
    # With an id, the repeat still collapses, which keeps graph payloads small.
    assert out["identified"] == {"a": {"id": "n1", "label": "N"}, "b": "n1"}
    assert out["cyclic"] == {"id": "c", "parent": "c"}


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_tooltip_templates_cannot_inject_markup():
    """Neither the template nor an interpolated value may become an element."""
    out = _run_node(
        _chart_js("reflexNivoSerialize")
        + _chart_js("reflexNivoTooltip")
        + """
        const reflexNivoCreateElement = (tag, props, ...children) => ({tag, children});
        const reflexNivoUseTheme = () => ({tooltip: {container: {}}});
        const render = (template, props) => reflexNivoTooltip(template, {})(props);
        console.log(JSON.stringify({
            allowed: render("<b>{id}</b><br/>{v}", {id: "x", v: 3}),
            valueWithScript: render("<b>{id}</b>", {id: "<script>alert(1)</script>"}),
            templateWithImg: render("<img src=x onerror=alert(1)>{id}", {id: "ok"}),
            templateWithHandler: render("<span onclick=alert(1)>{id}</span>", {id: "ok"}),
        }));
        """
    )
    # Whitelisted, attribute-less tags become real elements.
    assert out["allowed"]["children"][0] == {"tag": "b", "children": ["x"]}
    assert out["allowed"]["children"][1]["tag"] == "br"
    # A value is always a text child, never markup.
    assert out["valueWithScript"]["children"][0]["children"] == ["<script>alert(1)</script>"]
    # A tag carrying attributes stays literal text: no element, no handler.
    for case in ("templateWithImg", "templateWithHandler"):
        assert all(isinstance(child, str) for child in out[case]["children"]), out[case]


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


def test_key_goes_to_the_outer_element():
    """In rx.foreach the React key must be on the list item, the container."""
    container = nivo.bar(data=[], key="row-1")
    assert "row-1" in str(container)
    assert "row-1" not in str(_chart(container))
