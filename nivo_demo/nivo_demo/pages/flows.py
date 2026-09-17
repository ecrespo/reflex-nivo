"""Sankey, chord, network, parallel coordinates, funnel and marimekko."""

from __future__ import annotations

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, control, grid, page
from ..state import log


class FlowState(rx.State):
    sankey_align: str = "justify"
    link_gradient: bool = True
    marimekko_offset: str = "none"

    @rx.event
    def set_sankey_align(self, value: str):
        self.sankey_align = value

    @rx.event
    def set_link_gradient(self, value: bool):
        self.link_gradient = value

    @rx.event
    def set_marimekko_offset(self, value: str):
        self.marimekko_offset = value


def sankey_card() -> rx.Component:
    return chart_card(
        "Sankey",
        "nivo.sankey",
        nivo.sankey(
            data=data.sankey_data(),
            align=FlowState.sankey_align,
            colors=nivo.scheme("category10"),
            node_opacity=1,
            node_hover_others_opacity=0.35,
            node_thickness=18,
            node_spacing=24,
            node_border_width=0,
            node_border_radius=3,
            link_opacity=0.5,
            link_hover_others_opacity=0.1,
            link_contract=3,
            enable_link_gradient=FlowState.link_gradient,
            label_position="outside",
            label_orientation="horizontal",
            label_padding=16,
            label_text_color=nivo.inherit("color", ("darker", 1)),
            margin=nivo.margin(top=20, right=120, bottom=20, left=60),
            on_click=log("Sankey"),
            height="400px",
        ),
        control(
            "align",
            rx.select(
                ["justify", "start", "center", "end"],
                value=FlowState.sankey_align,
                on_change=FlowState.set_sankey_align,
                size="1",
            ),
        ),
        control(
            "gradient links",
            rx.switch(checked=FlowState.link_gradient, on_change=FlowState.set_link_gradient, size="1"),
        ),
        description="Nodes and links; clicking returns a node or link with cyclic references stripped.",
        span=2,
    )


def chord_card() -> rx.Component:
    return chart_card(
        "Chord",
        "nivo.chord",
        nivo.chord(
            data=data.chord_matrix(),
            keys=data.CHORD_KEYS,
            value_format=".2f",
            pad_angle=0.02,
            inner_radius_ratio=0.96,
            inner_radius_offset=0.02,
            arc_opacity=1,
            arc_border_width=1,
            arc_border_color=nivo.inherit("color", ("darker", 0.4)),
            ribbon_opacity=0.5,
            ribbon_border_width=1,
            ribbon_border_color=nivo.inherit("color", ("darker", 0.4)),
            label_offset=12,
            label_rotation=-90,
            label_text_color=nivo.inherit("color", ("darker", 1)),
            colors=nivo.scheme("nivo"),
            margin=nivo.margin(top=50, right=50, bottom=50, left=50),
            on_arc_click=log("Chord", "on_arc_click"),
            on_ribbon_click=log("Chord", "on_ribbon_click"),
            height="400px",
        ),
        description="Square matrix of flows; arc and ribbon click events.",
    )


def network_card() -> rx.Component:
    return chart_card(
        "Network",
        "nivo.network",
        nivo.network(
            data=data.network_data(),
            link_distance=nivo.js("(e) => e.distance"),
            centering_strength=0.3,
            repulsivity=6,
            node_size=nivo.js("(n) => n.size"),
            active_node_size=nivo.js("(n) => 1.5 * n.size"),
            node_color=nivo.js("(e) => e.color"),
            node_border_width=1,
            node_border_color=nivo.inherit("color", ("darker", 0.8)),
            link_thickness=nivo.js("(n) => 2 + 2 * n.target.data.height"),
            link_blend_mode="multiply",
            motion_config="wobbly",
            margin=nivo.margin(top=0, right=0, bottom=0, left=0),
            on_click=log("Network"),
            height="400px",
        ),
        description="Force layout; sizes/colors/distances from JS accessors (nivo.js).",
    )


def parallel_card() -> rx.Component:
    return chart_card(
        "Parallel coordinates",
        "nivo.parallel_coordinates",
        nivo.parallel_coordinates(
            data=data.parallel_data(),
            variables=data.PARALLEL_VARIABLES,
            group_by="kind",
            colors=nivo.scheme("set2"),
            line_width=2,
            line_opacity=0.6,
            curve="monotoneX",
            margin=nivo.margin(top=50, right=120, bottom=30, left=60),
            legends=[nivo.legend(anchor="right", translate_x=100, item_width=80)],
            height="380px",
        ),
        description="Multivariate lines grouped by category.",
    )


def funnel_card() -> rx.Component:
    return chart_card(
        "Funnel",
        "nivo.funnel",
        nivo.funnel(
            data=data.funnel_data(),
            value_format=">-.4s",
            colors=nivo.scheme("spectral"),
            border_width=20,
            label_color=nivo.inherit("color", ("darker", 3)),
            before_separator_length=60,
            before_separator_offset=20,
            after_separator_length=60,
            after_separator_offset=20,
            current_part_size_extension=10,
            current_border_width=40,
            motion_config="wobbly",
            margin=nivo.margin(top=20, right=20, bottom=20, left=20),
            on_click=log("Funnel"),
            height="380px",
        ),
        description="Conversion steps with separators and hover extension.",
    )


def marimekko_card() -> rx.Component:
    return chart_card(
        "Marimekko",
        "nivo.marimekko",
        nivo.marimekko(
            data=data.marimekko_data(),
            id_by="statement",
            value="participation",
            dimensions=data.MARIMEKKO_DIMENSIONS,
            layout="horizontal",
            offset=FlowState.marimekko_offset,
            inner_padding=9,
            border_width=1,
            border_color=nivo.inherit("color", ("darker", 0.2)),
            colors=nivo.scheme("red_yellow_green"),
            margin=nivo.margin(top=20, right=80, bottom=90, left=90),
            axis_bottom=nivo.axis(legend="responses", legend_offset=36, legend_position="middle"),
            axis_left=nivo.axis(legend="opinion", legend_offset=-80, legend_position="middle"),
            legends=[
                nivo.legend(
                    anchor="bottom", direction="row", translate_y=80, item_width=110, symbol_shape="square"
                )
            ],
            on_click=log("Marimekko"),
            height="400px",
        ),
        control(
            "offset",
            rx.select(
                ["none", "expand", "diverging", "silouhette", "wiggle"],
                value=FlowState.marimekko_offset,
                on_change=FlowState.set_marimekko_offset,
                size="1",
            ),
        ),
        description="Bar width encodes participation; stacks encode opinions.",
    )


def index() -> rx.Component:
    return page(
        "Flows & relations",
        "Links between entities and multi-dimensional comparisons.",
        grid(sankey_card(), chord_card(), network_card(), parallel_card(), funnel_card(), marimekko_card()),
    )
