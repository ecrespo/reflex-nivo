"""Pie, radar, radial bar, polar bar and waffle."""

from __future__ import annotations

import random
from typing import Any

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, control, grid, page
from ..state import EventLog, log


class RadialState(rx.State):
    pie: list[dict[str, Any]] = data.pie_data()
    inner_radius: float = 0.55
    pad_angle: float = 1.0
    corner_radius: int = 4
    active_id: str = ""
    radar_curve: str = "linearClosed"

    @rx.event
    def shuffle(self):
        self.pie = data.pie_data(seed=random.randint(0, 10_000))

    @rx.event
    def set_inner_radius(self, value: list[float]):
        self.inner_radius = value[0] / 100

    @rx.event
    def set_pad_angle(self, value: list[float]):
        self.pad_angle = value[0] / 10

    @rx.event
    def set_corner_radius(self, value: list[float]):
        self.corner_radius = int(value[0])

    @rx.event
    def set_radar_curve(self, value: str):
        self.radar_curve = value

    @rx.event
    def on_active_id(self, datum: Any):
        self.active_id = "" if datum is None else str(datum)

    @rx.event
    def pie_clicked(self, datum: dict[str, Any]):
        return EventLog.record("Pie", "on_click", datum)


PIE_CODE = """
nivo.pie(
    data=State.pie,                          # [{"id": .., "label": .., "value": ..}]
    inner_radius=State.inner_radius,         # 0 = pie, >0 = donut
    pad_angle=1,
    corner_radius=4,
    active_outer_radius_offset=8,
    arc_link_labels_color=nivo.inherit("color"),
    arc_labels_text_color=nivo.inherit("color", ("darker", 2)),
    tooltip=nivo.tooltip("<b>{datum.label}</b>: {datum.formattedValue}"),
    on_active_id_change=State.on_active_id,  # controlled/uncontrolled active arc
    on_click=State.pie_clicked,
)
"""


def pie_card() -> rx.Component:
    return chart_card(
        "Pie / donut",
        "nivo.pie",
        nivo.pie(
            data=RadialState.pie,
            inner_radius=RadialState.inner_radius,
            pad_angle=RadialState.pad_angle,
            corner_radius=RadialState.corner_radius,
            active_outer_radius_offset=8,
            border_width=1,
            border_color=nivo.inherit("color", ("darker", 0.2)),
            arc_link_labels_skip_angle=10,
            arc_link_labels_thickness=2,
            arc_link_labels_color=nivo.inherit("color"),
            arc_labels_skip_angle=10,
            arc_labels_text_color=nivo.inherit("color", ("darker", 2)),
            colors=nivo.scheme("paired"),
            margin=nivo.margin(top=30, right=80, bottom=30, left=80),
            tooltip=nivo.tooltip("<b>{datum.label}</b>: {datum.formattedValue}"),
            on_active_id_change=RadialState.on_active_id,
            on_click=RadialState.pie_clicked,
            height="360px",
        ),
        control(
            "inner radius",
            rx.slider(
                default_value=[55],
                min=0,
                max=90,
                on_value_commit=RadialState.set_inner_radius,
                width="90px",
                size="1",
            ),
        ),
        control(
            "pad",
            rx.slider(
                default_value=[10],
                min=0,
                max=50,
                on_value_commit=RadialState.set_pad_angle,
                width="80px",
                size="1",
            ),
        ),
        control(
            "corners",
            rx.slider(
                default_value=[4],
                min=0,
                max=20,
                on_value_commit=RadialState.set_corner_radius,
                width="80px",
                size="1",
            ),
        ),
        rx.button(
            rx.icon("shuffle", size=14), "Randomize", on_click=RadialState.shuffle, size="1", variant="soft"
        ),
        rx.badge(
            "active: ", rx.cond(RadialState.active_id != "", RadialState.active_id, "—"), variant="outline"
        ),
        description="Donut with template tooltip and on_active_id_change synced to state.",
        code=PIE_CODE,
    )


def radar_card() -> rx.Component:
    return chart_card(
        "Radar",
        "nivo.radar",
        nivo.radar(
            data=data.radar_data(),
            keys=["chardonay", "carmenere", "syrah"],
            index_by="taste",
            curve=RadialState.radar_curve,
            value_format=">-.2f",
            margin=nivo.margin(top=50, right=80, bottom=40, left=80),
            border_color=nivo.inherit("color"),
            grid_label_offset=24,
            dot_size=9,
            dot_color=nivo.from_theme("background"),
            dot_border_width=2,
            fill_opacity=0.25,
            blend_mode="multiply",
            colors=nivo.scheme("nivo"),
            legends=[
                nivo.legend(
                    anchor="top-left", translate_x=-60, translate_y=-40, item_width=80, item_height=18
                )
            ],
            on_click=log("Radar"),
            height="360px",
        ),
        control(
            "curve",
            rx.select(
                ["linearClosed", "basisClosed", "cardinalClosed", "catmullRomClosed"],
                value=RadialState.radar_curve,
                on_change=RadialState.set_radar_curve,
                size="1",
            ),
        ),
        description="Closed curves, dots and legends.",
    )


def radial_bar_card() -> rx.Component:
    return chart_card(
        "Radial bar",
        "nivo.radial_bar",
        nivo.radial_bar(
            data=data.radial_bar_data(),
            value_format=">-.2f",
            padding=0.35,
            corner_radius=3,
            end_angle=300,
            radial_axis_start={"tickSize": 5, "tickPadding": 5, "tickRotation": 0},
            circular_axis_outer={"tickSize": 5, "tickPadding": 12, "tickRotation": 0},
            colors=nivo.scheme("set2"),
            margin=nivo.margin(top=30, right=120, bottom=30, left=40),
            legends=[nivo.legend(anchor="right", translate_x=80, item_width=90, symbol_shape="square")],
            on_click=log("RadialBar"),
            height="360px",
        ),
        description="Stacked categories per serie around a circle.",
    )


def polar_bar_card() -> rx.Component:
    return chart_card(
        "Polar bar",
        "nivo.polar_bar",
        nivo.polar_bar(
            data=data.polar_bar_data(),
            keys=["rent", "groceries", "leisure"],
            index_by="month",
            value_steps=5,
            corner_radius=2,
            border_width=1,
            border_color=nivo.from_theme("background"),
            arc_labels_skip_radius=24,
            radial_axis={"angle": 180, "tickSize": 5, "tickPadding": 5},
            circular_axis_outer={"tickSize": 5, "tickPadding": 15},
            colors=nivo.scheme("pastel1"),
            margin=nivo.margin(top=30, right=20, bottom=70, left=20),
            legends=[
                nivo.legend(
                    anchor="bottom", direction="row", translate_y=50, item_width=90, symbol_shape="circle"
                )
            ],
            on_click=log("PolarBar"),
            height="400px",
        ),
        description="Monthly stacked arcs (new in nivo 0.99).",
    )


def waffle_card() -> rx.Component:
    return chart_card(
        "Waffle",
        "nivo.waffle",
        nivo.waffle(
            data=data.waffle_data(),
            total=100,
            rows=10,
            columns=18,
            padding=2,
            fill_direction="left",
            border_radius=3,
            colors=nivo.scheme("category10"),
            margin=nivo.margin(top=10, right=10, bottom=40, left=10),
            legends=[nivo.legend(anchor="bottom", direction="row", translate_y=36, item_width=90)],
            motion_config="wobbly",
            on_click=log("Waffle"),
            height="300px",
        ),
        description="Proportions out of a total on a grid.",
    )


def index() -> rx.Component:
    return page(
        "Pie & radial",
        "Arcs and polar coordinates: pie, radar, radial bar, polar bar and waffle.",
        grid(pie_card(), radar_card(), radial_bar_card(), polar_bar_card(), waffle_card()),
    )
