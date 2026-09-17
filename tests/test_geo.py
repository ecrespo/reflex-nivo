"""@nivo/geo only reads part of what its typings declare.

Verified against @nivo/geo@0.99.0 (dist/nivo-geo.mjs): GeoMap destructures
`onClick` alone, GeoMapCanvas `onClick` and `onMouseMove`, Choropleth `onClick`
plus `defs`/`fill`/`legends`, ChoroplethCanvas `onClick`, `onMouseMove` and
`legends`. Anything else a wrapper declares can never fire or take effect, so
the wrappers must not offer it. geo has no `onResize` either: its responsive
wrapper spreads props into the chart instead of the wrapper that reads it.
"""

from __future__ import annotations

import pytest
import reflex as rx
import reflex_nivo as nivo


class _State(rx.State):
    @rx.event
    def feature(self, datum: dict):
        pass

    @rx.event
    def noop(self):
        pass


@pytest.mark.parametrize(
    ("chart", "expected"),
    [
        (nivo.GeoMap, {"on_click"}),
        (nivo.GeoMapCanvas, {"on_click", "on_mouse_move"}),
        (nivo.Choropleth, {"on_click"}),
        (nivo.ChoroplethCanvas, {"on_click", "on_mouse_move"}),
    ],
    ids=lambda value: getattr(value, "__name__", str(value)),
)
def test_geo_declares_only_the_callbacks_nivo_reads(chart, expected):
    assert chart._nivo_event_names() == expected


@pytest.mark.parametrize(
    ("factory", "tag", "event", "dom_name"),
    [
        (nivo.geo_map, "ResponsiveGeoMap", "on_mouse_enter", "onMouseEnter"),
        (nivo.geo_map, "ResponsiveGeoMap", "on_mouse_move", "onMouseMove"),
        (nivo.geo_map, "ResponsiveGeoMap", "on_mouse_leave", "onMouseLeave"),
        (nivo.geo_map_canvas, "ResponsiveGeoMapCanvas", "on_mouse_enter", "onMouseEnter"),
        (nivo.geo_map_canvas, "ResponsiveGeoMapCanvas", "on_mouse_leave", "onMouseLeave"),
        (nivo.choropleth, "ResponsiveChoropleth", "on_mouse_enter", "onMouseEnter"),
        (nivo.choropleth, "ResponsiveChoropleth", "on_mouse_move", "onMouseMove"),
        (nivo.choropleth, "ResponsiveChoropleth", "on_mouse_leave", "onMouseLeave"),
        (nivo.choropleth_canvas, "ResponsiveChoroplethCanvas", "on_mouse_enter", "onMouseEnter"),
        (nivo.choropleth_canvas, "ResponsiveChoroplethCanvas", "on_mouse_leave", "onMouseLeave"),
    ],
)
def test_geo_sends_the_ignored_callbacks_to_the_container(factory, tag, event, dom_name):
    """A handler nivo would never call belongs on the <div>, where it fires."""
    container = factory(features=[], **{event: _State.noop})
    chart = str(container.children[0])
    assert dom_name not in chart, f"{tag} would swallow {event}"
    assert dom_name in str(container)


@pytest.mark.parametrize(
    ("chart", "absent"),
    [
        (nivo.GeoMap, {"defs", "fill", "legends"}),
        (nivo.GeoMapCanvas, {"defs", "fill", "legends"}),
        (nivo.ChoroplethCanvas, {"defs", "fill"}),
    ],
    ids=lambda value: getattr(value, "__name__", str(value)),
)
def test_geo_drops_props_nivo_never_reads(chart, absent):
    assert absent - set(chart.get_props()) == absent


@pytest.mark.parametrize(
    ("chart", "present"),
    [
        (nivo.Choropleth, {"defs", "fill", "legends"}),
        (nivo.ChoroplethCanvas, {"legends"}),
    ],
    ids=lambda value: getattr(value, "__name__", str(value)),
)
def test_geo_keeps_the_props_nivo_does_read(chart, present):
    assert present <= set(chart.get_props())
