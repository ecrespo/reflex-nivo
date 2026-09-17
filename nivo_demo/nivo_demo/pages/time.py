"""Calendar, time range, stream, bump, area bump and bullet."""

from __future__ import annotations

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, control, grid, page
from ..state import log


class TimeState(rx.State):
    offset_type: str = "wiggle"
    stream_curve: str = "catmullRom"
    calendar_direction: str = "horizontal"

    @rx.event
    def set_offset_type(self, value: str):
        self.offset_type = value

    @rx.event
    def set_stream_curve(self, value: str):
        self.stream_curve = value

    @rx.event
    def set_calendar_direction(self, value: str | list[str]):
        self.calendar_direction = str(value)


CALENDAR_CODE = """
nivo.calendar(
    data=[{"day": "2025-01-01", "value": 12}, ...],
    from_date="2025-01-01",      # nivo's `from` prop (Python keyword)
    to_date="2026-09-12",        # nivo's `to` prop
    empty_color="#eeeeee",
    colors=["#61cdbb", "#97e3d5", "#e8c1a0", "#f47560"],
    year_spacing=40,
    day_border_width=2,
    tooltip=nivo.tooltip("{day}: <b>{value}</b> commits"),
    on_click=State.day_clicked,
)
"""


def calendar_card() -> rx.Component:
    return chart_card(
        "Calendar",
        "nivo.calendar",
        nivo.calendar(
            data=data.calendar_data(),
            from_date="2025-01-01",
            to_date="2026-09-12",
            direction=TimeState.calendar_direction,
            empty_color=rx.color_mode_cond("#ebedf0", "#26282c"),
            colors=["#61cdbb", "#97e3d5", "#e8c1a0", "#f47560"],
            year_spacing=40,
            month_border_color=rx.color_mode_cond("#ffffff", "#111113"),
            day_border_width=2,
            day_border_color=rx.color_mode_cond("#ffffff", "#111113"),
            tooltip=nivo.tooltip("{day}: <b>{value}</b> commits"),
            legends=[
                nivo.legend(
                    anchor="bottom-right",
                    direction="row",
                    translate_y=36,
                    item_count=4,
                    item_width=42,
                    item_height=36,
                    items_spacing=14,
                    item_direction="right-to-left",
                    symbol_shape="square",
                )
            ],
            margin=nivo.margin(top=30, right=30, bottom=40, left=30),
            on_click=log("Calendar"),
            height=rx.cond(TimeState.calendar_direction == "horizontal", "340px", "900px"),
        ),
        control(
            "direction",
            rx.segmented_control.root(
                rx.segmented_control.item("horizontal", value="horizontal"),
                rx.segmented_control.item("vertical", value="vertical"),
                value=TimeState.calendar_direction,
                on_change=TimeState.set_calendar_direction,
                size="1",
            ),
        ),
        description="GitHub-style contributions over two years; from_date/to_date map to nivo's from/to.",
        code=CALENDAR_CODE,
        span=2,
    )


def time_range_card() -> rx.Component:
    return chart_card(
        "Time range",
        "nivo.time_range",
        nivo.time_range(
            data=data.calendar_data(seed=31, start=__import__("datetime").date(2026, 4, 1), days=160),
            from_date="2026-04-01",
            to_date="2026-09-07",
            empty_color=rx.color_mode_cond("#ebedf0", "#26282c"),
            colors=["#e0e7ff", "#a5b4fc", "#6366f1", "#3730a3"],
            day_radius=4,
            day_border_width=2,
            day_border_color=rx.color_mode_cond("#ffffff", "#111113"),
            weekday_ticks=[0, 2, 4, 6],
            margin=nivo.margin(top=40, right=40, bottom=20, left=40),
            on_click=log("TimeRange"),
            height="230px",
        ),
        description="Arbitrary date ranges with rounded days.",
        span=2,
    )


def stream_card() -> rx.Component:
    return chart_card(
        "Stream",
        "nivo.stream",
        nivo.stream(
            data=data.stream_data(),
            keys=["Raoul", "Josiane", "Marcel", "René", "Paul", "Jacques"],
            offset_type=TimeState.offset_type,
            curve=TimeState.stream_curve,
            colors=nivo.scheme("nivo"),
            fill_opacity=0.85,
            border_color=nivo.from_theme("background"),
            defs=[
                nivo.pattern_dots_def(
                    "dots", background="inherit", color="#2c998f", size=4, padding=2, stagger=True
                ),
                nivo.pattern_lines_def(
                    "lines", background="inherit", color="#e4c912", rotation=-45, line_width=6, spacing=10
                ),
            ],
            fill=[nivo.fill_rule("dots", {"id": "Paul"}), nivo.fill_rule("lines", {"id": "Marcel"})],
            enable_grid_x=True,
            enable_grid_y=False,
            dot_size=8,
            margin=nivo.margin(top=20, right=110, bottom=50, left=60),
            axis_bottom=nivo.axis(legend="week", legend_offset=36, legend_position="middle"),
            legends=[
                nivo.legend(anchor="bottom-right", translate_x=100, item_width=80, symbol_shape="circle")
            ],
            height="360px",
        ),
        control(
            "offset",
            rx.select(
                ["wiggle", "silhouette", "expand", "none", "diverging", "insideOut"],
                value=TimeState.offset_type,
                on_change=TimeState.set_offset_type,
                size="1",
            ),
        ),
        control(
            "curve",
            rx.select(
                list(nivo.CURVES),
                value=TimeState.stream_curve,
                on_change=TimeState.set_stream_curve,
                size="1",
            ),
        ),
        description="Offsets, curves and SVG patterns matched per layer.",
    )


def bump_card() -> rx.Component:
    return chart_card(
        "Bump",
        "nivo.bump",
        nivo.bump(
            data=data.bump_data(),
            colors=nivo.scheme("category10"),
            line_width=3,
            active_line_width=6,
            inactive_line_width=3,
            inactive_opacity=0.15,
            point_size=10,
            active_point_size=16,
            inactive_point_size=0,
            point_color=nivo.from_theme("background"),
            point_border_width=3,
            active_point_border_width=3,
            point_border_color=nivo.inherit("serie.color"),
            axis_top=nivo.axis(tick_size=5, tick_padding=5),
            axis_bottom=nivo.axis(
                tick_size=5, tick_padding=5, legend="season", legend_position="middle", legend_offset=32
            ),
            axis_left=nivo.axis(
                tick_size=5, tick_padding=5, legend="ranking", legend_position="middle", legend_offset=-40
            ),
            margin=nivo.margin(top=40, right=100, bottom=40, left=60),
            on_click=log("Bump"),
            height="360px",
        ),
        description="Rankings over seasons; hover isolates a serie.",
    )


def area_bump_card() -> rx.Component:
    return chart_card(
        "Area bump",
        "nivo.area_bump",
        nivo.area_bump(
            data=data.area_bump_data(),
            align="middle",
            spacing=8,
            x_padding=0.3,
            colors=nivo.scheme("nivo"),
            blend_mode="multiply",
            start_label=nivo.template("{id}"),
            end_label=nivo.template("{id}"),
            axis_top=nivo.axis(tick_size=5, tick_padding=5),
            axis_bottom=nivo.axis(
                tick_size=5, tick_padding=5, legend="year", legend_position="middle", legend_offset=32
            ),
            margin=nivo.margin(top=40, right=100, bottom=40, left=100),
            on_click=log("AreaBump"),
            height="360px",
        ),
        description="Ranking and magnitude together.",
    )


def bullet_card() -> rx.Component:
    return chart_card(
        "Bullet",
        "nivo.bullet",
        nivo.bullet(
            data=data.bullet_data(),
            spacing=46,
            title_align="start",
            title_offset_x=-80,
            measure_size=0.3,
            marker_size=0.8,
            range_colors=["#e0e7ff", "#c7d2fe", "#a5b4fc"],
            measure_colors=["#3e63dd", "#e5484d"],
            marker_colors=["#f76b15"],
            margin=nivo.margin(top=40, right=40, bottom=40, left=100),
            on_measure_click=log("Bullet", "on_measure_click"),
            on_range_click=log("Bullet", "on_range_click"),
            on_marker_click=log("Bullet", "on_marker_click"),
            height="340px",
        ),
        description="KPIs versus qualitative ranges and targets.",
        span=2,
    )


def index() -> rx.Component:
    return page(
        "Time",
        "Temporal views: calendars, streams, rankings and KPI bullets.",
        grid(calendar_card(), time_range_card(), stream_card(), bump_card(), area_bump_card(), bullet_card()),
    )
