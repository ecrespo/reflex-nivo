"""Choropleth and GeoMap."""

from __future__ import annotations

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, control, grid, page
from ..state import log


class GeoState(rx.State):
    projection: str = "naturalEarth1"
    graticule: bool = True
    rotation: int = 0
    scheme: str = "blues"

    @rx.event
    def set_projection(self, value: str):
        self.projection = value

    @rx.event
    def set_graticule(self, value: bool):
        self.graticule = value

    @rx.event
    def set_rotation(self, value: list[float]):
        self.rotation = int(value[0])

    @rx.event
    def set_scheme(self, value: str):
        self.scheme = value

    @rx.var
    def projection_scale(self) -> int:
        return {"orthographic": 220, "mercator": 110, "equirectangular": 140}.get(self.projection, 150)


GEO_CODE = """
features = json.loads(Path("world_countries.json").read_text())["features"]

nivo.choropleth(
    features=features,                       # GeoJSON features with an `id`
    data=[{"id": "VEN", "value": 523_000}],  # matched on feature id
    domain=[0, 1_000_000],
    colors="blues",
    unknown_color="#666666",
    label="properties.name",
    value_format=".2s",
    projection_type="naturalEarth1",
    projection_scale=150,
    projection_translation=[0.5, 0.5],
    projection_rotation=[0, 0, 0],
    enable_graticule=True,
    border_width=0.5,
    legends=[nivo.legend(anchor="bottom-left", translate_x=20, translate_y=-60)],
    on_click=State.country_clicked,
)
"""

PROJECTIONS = [
    "naturalEarth1",
    "equalEarth",
    "mercator",
    "equirectangular",
    "orthographic",
    "azimuthalEqualArea",
    "azimuthalEquidistant",
    "stereographic",
    "transverseMercator",
    "gnomonic",
]


def choropleth_card() -> rx.Component:
    return chart_card(
        "Choropleth",
        "nivo.choropleth",
        nivo.choropleth(
            features=data.world_features(),
            data=data.choropleth_data(),
            domain=[0, 1_000_000],
            colors=GeoState.scheme,
            unknown_color="#666666",
            label="properties.name",
            value_format=".2s",
            projection_type=GeoState.projection,
            projection_scale=GeoState.projection_scale,
            projection_translation=[0.5, 0.5],
            projection_rotation=rx.Var.create([GeoState.rotation, 0, 0]),
            enable_graticule=GeoState.graticule,
            graticule_line_color=rx.color_mode_cond("#dddddd", "#3a3d42"),
            border_width=0.5,
            border_color=rx.color_mode_cond("#152538", "#111113"),
            legends=[
                nivo.legend(
                    anchor="bottom-left",
                    direction="column",
                    translate_x=20,
                    translate_y=-40,
                    item_width=94,
                    item_height=18,
                    symbol_size=18,
                    effects=[nivo.hover_effect(item_text_color="#e5484d", item_opacity=1)],
                )
            ],
            margin=nivo.margin(),
            on_click=log("Choropleth"),
            height="520px",
        ),
        control(
            "projection",
            rx.select(PROJECTIONS, value=GeoState.projection, on_change=GeoState.set_projection, size="1"),
        ),
        control(
            "scheme",
            rx.select(
                list(nivo.SEQUENTIAL_COLOR_SCHEMES),
                value=GeoState.scheme,
                on_change=GeoState.set_scheme,
                size="1",
            ),
        ),
        control(
            "rotate λ",
            rx.slider(
                default_value=[0],
                min=-180,
                max=180,
                on_value_commit=GeoState.set_rotation,
                width="120px",
                size="1",
            ),
        ),
        control(
            "graticule", rx.switch(checked=GeoState.graticule, on_change=GeoState.set_graticule, size="1")
        ),
        description="176 countries, 10 d3-geo projections, sequential scheme and legend.",
        code=GEO_CODE,
        span=2,
    )


def geomap_card() -> rx.Component:
    return chart_card(
        "GeoMap (orthographic globe)",
        "nivo.geo_map",
        nivo.geo_map(
            features=data.world_features(),
            projection_type="orthographic",
            projection_scale=180,
            projection_rotation=[70, -8, 0],
            fill_color=rx.color_mode_cond("#c7d2fe", "#3e4a89"),
            border_width=0.5,
            border_color=rx.color_mode_cond("#4338ca", "#a5b4fc"),
            enable_graticule=True,
            graticule_line_color=rx.color_mode_cond("#e0e7ff", "#2b2f45"),
            margin=nivo.margin(),
            on_click=log("GeoMap"),
            height="420px",
        ),
        description="Plain features, no data binding (centered on the Americas).",
    )


def geomap_canvas_card() -> rx.Component:
    return chart_card(
        "Choropleth on canvas",
        "nivo.choropleth_canvas",
        nivo.choropleth_canvas(
            features=data.world_features(),
            data=data.choropleth_data(seed=3),
            domain=[0, 1_000_000],
            colors="YlOrRd",
            unknown_color="#666666",
            label="properties.name",
            value_format=".2s",
            projection_type="equalEarth",
            projection_scale=120,
            border_width=0.3,
            border_color="#222222",
            margin=nivo.margin(),
            on_click=log("ChoroplethCanvas"),
            height="420px",
        ),
        description="Same API rendered on canvas (d3 color scheme names are accepted too).",
    )


def index() -> rx.Component:
    return page(
        "Geo",
        "GeoJSON features rendered with d3-geo projections.",
        grid(choropleth_card(), geomap_card(), geomap_canvas_card()),
    )
