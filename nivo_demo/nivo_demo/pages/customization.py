"""Themes, tooltips, formatters, patterns, markers, annotations and layers."""

from __future__ import annotations

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, control, grid, page
from ..state import log


class CustomState(rx.State):
    tooltip_template: str = "<b>{indexValue}</b> · {id}\n{formattedValue} kcal"
    font_size: int = 12
    grid_color: str = "#d9d9e0"
    text_color: str = "#6e56cf"
    show_grid: bool = True

    @rx.event
    def set_tooltip_template(self, value: str):
        self.tooltip_template = value

    @rx.event
    def set_font_size(self, value: list[float]):
        self.font_size = int(value[0])

    @rx.event
    def set_grid_color(self, value: str):
        self.grid_color = value

    @rx.event
    def set_text_color(self, value: str):
        self.text_color = value

    @rx.event
    def set_show_grid(self, value: bool):
        self.show_grid = value

    @rx.var
    def theme(self) -> dict:
        return nivo.themes.merge(
            nivo.themes.LIGHT,
            {
                "background": "#fbfaff",
                "text": {"fontSize": self.font_size, "fill": self.text_color},
                "axis": {"ticks": {"text": {"fontSize": self.font_size, "fill": self.text_color}}},
                "grid": {"line": {"stroke": self.grid_color, "strokeDasharray": "4 4"}},
            },
        )

    @rx.var
    def layers(self) -> list[str]:
        base = ["axes", "bars", "markers", "legends", "annotations"]
        return ["grid", *base] if self.show_grid else base


TOOLTIP_CODE = """
nivo.bar(
    ...,
    # {path} placeholders are read from the object nivo passes to the tooltip.
    # Values are HTML-escaped, the template may contain markup.
    tooltip=nivo.tooltip(State.template, style={"border_left": "4px solid #6e56cf"}),
    value_format=nivo.js("v => `${v.toLocaleString()} kcal`"),
    axis_left=nivo.axis(format=nivo.js("v => `${v / 1000}k`")),
)
"""

THEME_CODE = """
# Default: charts follow Reflex's color mode (nivo.themes.auto()).
nivo.line(..., theme=nivo.themes.auto({"grid": {"line": {"strokeDasharray": "4 4"}}}))

# Any partial nivo theme dict (or a computed var) works too:
nivo.bar(..., theme=State.theme, layers=State.layers)
"""


def tooltip_card() -> rx.Component:
    return chart_card(
        "Template tooltips & JS formatters",
        "nivo.tooltip · nivo.js",
        nivo.bar(
            data=data.bar_data(seed=8),
            keys=["burger", "fries", "donut"],
            index_by="country",
            group_mode="grouped",
            colors=nivo.scheme("set2"),
            padding=0.25,
            inner_padding=2,
            border_radius=3,
            enable_label=False,
            value_format=nivo.js("(v) => `${Number(v).toLocaleString()} kcal`"),
            axis_left=nivo.axis(format=nivo.js("(v) => `${v}`.padStart(3, '0')")),
            tooltip=nivo.tooltip(CustomState.tooltip_template, style={"border_left": "4px solid #6e56cf"}),
            margin=nivo.margin(top=10, right=10, bottom=40, left=50),
            on_click=log("Bar (tooltip)"),
            height="320px",
        ),
        rx.input(
            value=CustomState.tooltip_template,
            on_change=CustomState.set_tooltip_template,
            size="1",
            width="100%",
            font_family="monospace",
        ),
        description="Edit the template: the tooltip updates live. Try {data.fries} or {color}.",
        code=TOOLTIP_CODE,
    )


def theme_card() -> rx.Component:
    return chart_card(
        "Custom theme & layers",
        "theme=State.theme",
        nivo.line(
            data=data.line_data(seed=77)[:3],
            x_scale=nivo.scale("point"),
            y_scale=nivo.scale("linear", min="auto", max="auto"),
            theme=CustomState.theme,
            layers=[
                "grid",
                "markers",
                "axes",
                "areas",
                "crosshair",
                "lines",
                "points",
                "slices",
                "mesh",
                "legends",
            ],
            enable_grid_x=CustomState.show_grid,
            enable_grid_y=CustomState.show_grid,
            curve="natural",
            point_size=7,
            colors=["#6e56cf", "#12a594", "#f76b15"],
            use_mesh=True,
            margin=nivo.margin(top=20, right=20, bottom=40, left=50),
            height="320px",
        ),
        control(
            "font",
            rx.slider(
                default_value=[12],
                min=9,
                max=18,
                on_value_commit=CustomState.set_font_size,
                width="80px",
                size="1",
            ),
        ),
        control(
            "text",
            rx.input(
                type="color",
                value=CustomState.text_color,
                on_change=CustomState.set_text_color,
                width="44px",
                size="1",
                padding="0",
            ),
        ),
        control(
            "grid",
            rx.input(
                type="color",
                value=CustomState.grid_color,
                on_change=CustomState.set_grid_color,
                width="44px",
                size="1",
                padding="0",
            ),
        ),
        control(
            "show grid",
            rx.switch(checked=CustomState.show_grid, on_change=CustomState.set_show_grid, size="1"),
        ),
        description="A theme dict computed in Python from state (fixed light background).",
        code=THEME_CODE,
    )


def patterns_card() -> rx.Component:
    return chart_card(
        "Patterns & gradients",
        "defs + fill",
        nivo.bar(
            data=data.bar_data(seed=3)[:5],
            keys=["hot dog", "burger", "sandwich"],
            index_by="country",
            colors=nivo.scheme("nivo"),
            defs=[
                nivo.pattern_dots_def(
                    "dots", background="inherit", color="#38bcb2", size=4, padding=1, stagger=True
                ),
                nivo.pattern_lines_def(
                    "lines", background="inherit", color="#eed312", rotation=-45, line_width=6, spacing=10
                ),
                nivo.pattern_squares_def(
                    "squares", background="inherit", color="rgba(255,255,255,.4)", size=5, padding=2
                ),
                nivo.linear_gradient_def(
                    "gradient",
                    [{"offset": 0, "color": "inherit"}, {"offset": 100, "color": "inherit", "opacity": 0.3}],
                ),
            ],
            fill=[
                nivo.fill_rule("dots", {"id": "hot dog"}),
                nivo.fill_rule("lines", {"id": "burger"}),
                nivo.fill_rule("squares", {"indexValue": "AF"}),
                nivo.fill_rule("gradient", {"id": "sandwich"}),
            ],
            border_color=nivo.inherit("color", ("darker", 1.2)),
            border_width=1,
            label_skip_height=16,
            margin=nivo.margin(top=10, right=10, bottom=40, left=50),
            height="320px",
        ),
        description="SVG defs matched to datums by id or index value.",
    )


def annotations_card() -> rx.Component:
    return chart_card(
        "Markers & annotations",
        "nivo.marker · nivo.annotation",
        nivo.scatterplot(
            data=data.scatter_data(seed=9, groups=2, points=30),
            node_size=10,
            colors=["#0090ff", "#e54666"],
            markers=[
                nivo.marker(
                    "x",
                    40,
                    legend="x = 40",
                    legend_orientation="vertical",
                    line_style={"stroke": "#8b8d98", "strokeDasharray": "6 4"},
                ),
                nivo.marker(
                    "y",
                    50,
                    legend="target",
                    legend_position="bottom-right",
                    line_style={"stroke": "#30a46c", "strokeWidth": 2},
                ),
            ],
            annotations=[
                nivo.annotation(
                    {"serieId": "group A", "index": 3},
                    type_="circle",
                    note="an outlier?",
                    note_x=40,
                    note_y=-30,
                    note_width=10,
                ),
                nivo.annotation(
                    {"serieId": "group B", "index": 7},
                    type_="dot",
                    note="interesting",
                    note_x=-40,
                    note_y=40,
                    note_width=10,
                ),
            ],
            x_scale=nivo.scale("linear", min=0, max=80),
            y_scale=nivo.scale("linear", min=0, max=100),
            margin=nivo.margin(top=20, right=20, bottom=40, left=50),
            height="320px",
        ),
        description="Cartesian markers and annotations matching specific nodes.",
    )


def themes_side_by_side() -> rx.Component:
    kwargs = {
        "data": data.pie_data(seed=4),
        "inner_radius": 0.6,
        "pad_angle": 2,
        "corner_radius": 4,
        "colors": nivo.scheme("set2"),
        "arc_link_labels_color": nivo.inherit("color"),
        "margin": nivo.margin(top=24, right=70, bottom=24, left=70),
        "height": "240px",
    }
    return chart_card(
        "Explicit light & dark themes",
        "nivo.themes.LIGHT / DARK",
        rx.grid(
            rx.box(nivo.pie(theme=nivo.themes.LIGHT, **kwargs), background="#ffffff", border_radius="8px"),
            rx.box(nivo.pie(theme=nivo.themes.DARK, **kwargs), background="#111113", border_radius="8px"),
            columns="2",
            gap="12px",
            width="100%",
        ),
        description="Pin a theme regardless of the app color mode.",
        span=2,
    )


def index() -> rx.Component:
    return page(
        "Customization",
        "Everything nivo lets you customize is reachable from Python: themes, tooltips, formatters, patterns, markers, annotations, layers.",
        grid(tooltip_card(), theme_card(), patterns_card(), annotations_card(), themes_side_by_side()),
    )
