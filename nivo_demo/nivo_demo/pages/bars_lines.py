"""Bar and line charts with live controls."""

from __future__ import annotations

import random
from typing import Any

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, control, grid, page
from ..state import log


class BarLineState(rx.State):
    bars: list[dict[str, Any]] = data.bar_data()
    group_mode: str = "stacked"
    layout: str = "vertical"
    scheme: str = "nivo"
    padding: float = 0.3
    border_radius: int = 2
    enable_totals: bool = True

    lines: list[dict[str, Any]] = data.line_data()
    curve: str = "monotoneX"
    enable_area: bool = False
    enable_points: bool = True
    enable_slices: bool = False

    @rx.event
    def shuffle_bars(self):
        self.bars = data.bar_data(seed=random.randint(0, 10_000))

    @rx.event
    def shuffle_lines(self):
        self.lines = data.line_data(seed=random.randint(0, 10_000))

    @rx.event
    def set_padding(self, value: list[float]):
        self.padding = value[0] / 100

    @rx.event
    def set_border_radius(self, value: list[float]):
        self.border_radius = int(value[0])

    @rx.event
    def set_group_mode(self, value: str | list[str]):
        self.group_mode = str(value)

    @rx.event
    def set_layout(self, value: str | list[str]):
        self.layout = str(value)

    @rx.event
    def set_scheme(self, value: str):
        self.scheme = value

    @rx.event
    def set_enable_totals(self, value: bool):
        self.enable_totals = value

    @rx.event
    def set_curve(self, value: str):
        self.curve = value

    @rx.event
    def set_enable_area(self, value: bool):
        self.enable_area = value

    @rx.event
    def set_enable_points(self, value: bool):
        self.enable_points = value

    @rx.event
    def set_enable_slices(self, value: bool):
        self.enable_slices = value


BAR_CODE = """
nivo.bar(
    data=State.bars,
    keys=["hot dog", "burger", "sandwich", "kebab", "fries", "donut"],
    index_by="country",
    group_mode=State.group_mode,        # "stacked" | "grouped"
    layout=State.layout,                # "vertical" | "horizontal"
    colors=nivo.scheme("nivo"),
    padding=0.3,
    enable_totals=True,
    margin=nivo.margin(top=30, right=130, bottom=50, left=60),
    axis_bottom=nivo.axis(legend="country", legend_position="middle", legend_offset=36),
    legends=[nivo.legend(data_from="keys", anchor="bottom-right", translate_x=120)],
    on_click=State.handle_click,        # receives the clicked datum as a dict
    height="440px",
)
"""

LINE_CODE = """
nivo.line(
    data=State.lines,                   # [{"id": ..., "data": [{"x": .., "y": ..}]}]
    x_scale=nivo.scale("point"),
    y_scale=nivo.scale("linear", min="auto", max="auto"),
    curve="monotoneX",
    enable_area=True,
    use_mesh=True,
    enable_slices="x",                  # or False
    point_size=8,
    point_border_width=2,
    point_border_color=nivo.inherit("serieColor"),
    legends=[nivo.legend(anchor="bottom-right", translate_x=100)],
)
"""


def bar_card() -> rx.Component:
    return chart_card(
        "Bar",
        "nivo.bar",
        nivo.bar(
            data=BarLineState.bars,
            keys=data.FOODS,
            index_by="country",
            group_mode=BarLineState.group_mode,
            layout=BarLineState.layout,
            colors=nivo.scheme(BarLineState.scheme),
            padding=BarLineState.padding,
            border_radius=BarLineState.border_radius,
            enable_totals=BarLineState.enable_totals,
            label_skip_height=14,
            label_text_color=nivo.inherit("color", ("darker", 1.8)),
            margin=nivo.margin(top=30, right=130, bottom=50, left=60),
            axis_bottom=nivo.axis(legend="country", legend_position="middle", legend_offset=36),
            axis_left=nivo.axis(legend="food", legend_position="middle", legend_offset=-45),
            legends=[
                nivo.legend(
                    data_from="keys",
                    anchor="bottom-right",
                    translate_x=120,
                    item_width=100,
                    symbol_shape="square",
                    toggle_serie=True,
                    effects=[nivo.hover_effect(item_opacity=0.6)],
                )
            ],
            role="application",
            aria_label="Food consumption per country",
            on_click=log("Bar"),
            height="440px",
        ),
        control(
            "mode",
            rx.segmented_control.root(
                rx.segmented_control.item("stacked", value="stacked"),
                rx.segmented_control.item("grouped", value="grouped"),
                value=BarLineState.group_mode,
                on_change=BarLineState.set_group_mode,
                size="1",
            ),
        ),
        control(
            "layout",
            rx.segmented_control.root(
                rx.segmented_control.item("vertical", value="vertical"),
                rx.segmented_control.item("horizontal", value="horizontal"),
                value=BarLineState.layout,
                on_change=BarLineState.set_layout,
                size="1",
            ),
        ),
        control(
            "scheme",
            rx.select(
                list(nivo.CATEGORICAL_COLOR_SCHEMES),
                value=BarLineState.scheme,
                on_change=BarLineState.set_scheme,
                size="1",
            ),
        ),
        control(
            "padding",
            rx.slider(
                default_value=[30],
                min=0,
                max=90,
                on_value_commit=BarLineState.set_padding,
                width="90px",
                size="1",
            ),
        ),
        control(
            "radius",
            rx.slider(
                default_value=[2],
                min=0,
                max=12,
                on_value_commit=BarLineState.set_border_radius,
                width="90px",
                size="1",
            ),
        ),
        control(
            "totals",
            rx.switch(checked=BarLineState.enable_totals, on_change=BarLineState.set_enable_totals, size="1"),
        ),
        rx.button(
            rx.icon("shuffle", size=14),
            "Randomize",
            on_click=BarLineState.shuffle_bars,
            size="1",
            variant="soft",
        ),
        description="Stacked/grouped, vertical/horizontal, legends that toggle series, click events.",
        code=BAR_CODE,
        span=2,
    )


def line_card() -> rx.Component:
    return chart_card(
        "Line",
        "nivo.line",
        nivo.line(
            data=BarLineState.lines,
            x_scale=nivo.scale("point"),
            y_scale=nivo.scale("linear", min="auto", max="auto", stacked=False),
            curve=BarLineState.curve,
            enable_area=BarLineState.enable_area,
            area_opacity=0.12,
            enable_points=BarLineState.enable_points,
            point_size=8,
            point_color=nivo.from_theme("background"),
            point_border_width=2,
            point_border_color=nivo.inherit("seriesColor"),
            use_mesh=True,
            enable_slices=rx.cond(BarLineState.enable_slices, "x", False),
            colors=nivo.scheme("category10"),
            margin=nivo.margin(top=20, right=110, bottom=50, left=60),
            axis_bottom=nivo.axis(legend="month", legend_offset=36, legend_position="middle"),
            axis_left=nivo.axis(legend="value", legend_offset=-45, legend_position="middle"),
            legends=[nivo.legend(anchor="bottom-right", translate_x=100, item_width=80, toggle_serie=True)],
            on_click=log("Line"),
            height="400px",
        ),
        control(
            "curve",
            rx.select(
                list(nivo.CURVES), value=BarLineState.curve, on_change=BarLineState.set_curve, size="1"
            ),
        ),
        control(
            "area",
            rx.switch(checked=BarLineState.enable_area, on_change=BarLineState.set_enable_area, size="1"),
        ),
        control(
            "points",
            rx.switch(checked=BarLineState.enable_points, on_change=BarLineState.set_enable_points, size="1"),
        ),
        control(
            "slices",
            rx.switch(checked=BarLineState.enable_slices, on_change=BarLineState.set_enable_slices, size="1"),
        ),
        rx.button(
            rx.icon("shuffle", size=14),
            "Randomize",
            on_click=BarLineState.shuffle_lines,
            size="1",
            variant="soft",
        ),
        description="Point scale, curves, areas, slices tooltip and mesh interaction.",
        code=LINE_CODE,
        span=2,
    )


def time_line_card() -> rx.Component:
    return chart_card(
        "Line with a time scale",
        "nivo.line",
        nivo.line(
            data=data.time_series(),
            x_scale=nivo.scale("time", format="%Y-%m-%d", use_utc=False, precision="day"),
            x_format="time:%Y-%m-%d",
            y_scale=nivo.scale("linear", stacked=False),
            axis_bottom=nivo.axis(
                format="%b %d",
                tick_values="every 2 weeks",
                legend="date",
                legend_offset=36,
                legend_position="middle",
            ),
            axis_left=nivo.axis(legend="count", legend_offset=-45, legend_position="middle"),
            enable_points=False,
            enable_area=True,
            area_opacity=0.08,
            use_mesh=True,
            enable_crosshair=True,
            curve="basis",
            markers=[
                nivo.marker(
                    "y",
                    400,
                    legend="SLO",
                    line_style={"stroke": "#e5484d", "strokeWidth": 1, "strokeDasharray": "4 4"},
                )
            ],
            colors=["#3e63dd", "#e5484d"],
            margin=nivo.margin(top=20, right=20, bottom=50, left=60),
            on_click=log("Line (time)"),
            height="320px",
        ),
        description="ISO dates parsed by a time scale, d3 time formats and a marker.",
    )


def stacked_area_card() -> rx.Component:
    return chart_card(
        "Stacked areas + gradients",
        "nivo.line",
        nivo.line(
            data=data.line_data(seed=42),
            x_scale=nivo.scale("point"),
            y_scale=nivo.scale("linear", stacked=True),
            enable_area=True,
            area_opacity=0.9,
            enable_points=False,
            curve="catmullRom",
            defs=[
                nivo.linear_gradient_def(
                    "fade",
                    [{"offset": 0, "color": "inherit"}, {"offset": 100, "color": "inherit", "opacity": 0.15}],
                )
            ],
            fill=[nivo.fill_rule("fade")],
            use_mesh=True,
            colors=nivo.scheme("set2"),
            margin=nivo.margin(top=20, right=20, bottom=40, left=50),
            height="320px",
        ),
        description="y_scale stacked, SVG gradient defs matched with fill rules.",
    )


def index() -> rx.Component:
    return page(
        "Bars & lines",
        "The two workhorses. Every control below is plain Reflex state bound to nivo props.",
        grid(bar_card(), line_card(), time_line_card(), stacked_area_card()),
    )
