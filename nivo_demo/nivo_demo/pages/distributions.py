"""Scatter, swarm, box plot, heatmap and voronoi."""

from __future__ import annotations

import random
from typing import Any

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, control, grid, page
from ..state import log


class DistributionState(rx.State):
    heat: list[dict[str, Any]] = data.heatmap_data()
    heat_scheme: str = "red_yellow_blue"
    swarm_layout: str = "vertical"
    voronoi_cells: bool = True
    voronoi_links: bool = False

    @rx.event
    def shuffle_heat(self):
        self.heat = data.heatmap_data(seed=random.randint(0, 10_000))

    @rx.event
    def set_heat_scheme(self, value: str):
        self.heat_scheme = value

    @rx.event
    def set_swarm_layout(self, value: str | list[str]):
        self.swarm_layout = str(value)

    @rx.event
    def set_voronoi_cells(self, value: bool):
        self.voronoi_cells = value

    @rx.event
    def set_voronoi_links(self, value: bool):
        self.voronoi_links = value


HEATMAP_CODE = """
nivo.heatmap(
    data=State.heat,                      # [{"id": "Mon", "data": [{"x": "00h", "y": 12}]}]
    colors={"type": "diverging", "scheme": State.scheme, "divergeAt": 0.5, "minValue": -100, "maxValue": 100},
    value_format=">-.0f",
    empty_color="#555555",
    axis_top=nivo.axis(tick_rotation=-90),
    legends=[{"anchor": "bottom", "translateY": 30, "length": 400, "thickness": 8,
              "direction": "row", "tickPosition": "after", "title": "Value →"}],
    on_click=State.cell_clicked,
)
"""


def scatter_card() -> rx.Component:
    return chart_card(
        "Scatter plot",
        "nivo.scatterplot",
        nivo.scatterplot(
            data=data.scatter_data(),
            x_scale=nivo.scale("linear", min=0, max="auto"),
            y_scale=nivo.scale("linear", min=0, max="auto"),
            x_format=">-.1f",
            y_format=">-.1f",
            node_size=9,
            colors=nivo.scheme("category10"),
            blend_mode="multiply",
            use_mesh=True,
            margin=nivo.margin(top=20, right=110, bottom=50, left=60),
            axis_bottom=nivo.axis(legend="weight", legend_position="middle", legend_offset=36),
            axis_left=nivo.axis(legend="size", legend_position="middle", legend_offset=-45),
            legends=[nivo.legend(anchor="bottom-right", translate_x=100, item_width=80)],
            tooltip=nivo.tooltip("<b>{node.serieId}</b>\nx: {node.formattedX}\ny: {node.formattedY}"),
            on_click=log("ScatterPlot"),
            height="360px",
        ),
        description="Linear scales, mesh interaction and a template tooltip.",
    )


def swarm_card() -> rx.Component:
    return chart_card(
        "Swarm plot",
        "nivo.swarmplot",
        nivo.swarmplot(
            data=data.swarm_data(),
            groups=["group A", "group B", "group C"],
            group_by="group",
            value="price",
            value_format="$.2f",
            value_scale=nivo.scale("linear", min=0, max=450, reverse=False),
            size={"key": "volume", "values": [4, 20], "sizes": [6, 20]},
            layout=DistributionState.swarm_layout,
            force_strength=4,
            simulation_iterations=100,
            colors=nivo.scheme("set2"),
            border_color=nivo.inherit("color", ("darker", 0.6), ("opacity", 0.5)),
            margin=nivo.margin(top=40, right=40, bottom=60, left=70),
            axis_bottom=nivo.axis(legend="group", legend_position="middle", legend_offset=40),
            axis_left=nivo.axis(legend="price", legend_position="middle", legend_offset=-55),
            on_click=log("SwarmPlot"),
            height="360px",
        ),
        control(
            "layout",
            rx.segmented_control.root(
                rx.segmented_control.item("vertical", value="vertical"),
                rx.segmented_control.item("horizontal", value="horizontal"),
                value=DistributionState.swarm_layout,
                on_change=DistributionState.set_swarm_layout,
                size="1",
            ),
        ),
        description="Force simulation; node size bound to the volume field.",
    )


def boxplot_card() -> rx.Component:
    return chart_card(
        "Box plot",
        "nivo.boxplot",
        nivo.boxplot(
            data=data.boxplot_data(),
            group_by="group",
            sub_group_by="subgroup",
            quantiles=[0.1, 0.25, 0.5, 0.75, 0.9],
            min_value=0,
            max_value=30,
            padding=0.12,
            enable_grid_x=True,
            colors=nivo.scheme("nivo"),
            border_width=2,
            border_color=nivo.inherit("color", ("darker", 0.3)),
            median_width=2,
            median_color=nivo.inherit("color", ("darker", 0.3)),
            whisker_end_size=0.6,
            whisker_color=nivo.inherit("color", ("darker", 0.3)),
            margin=nivo.margin(top=40, right=110, bottom=60, left=60),
            axis_bottom=nivo.axis(legend="group", legend_position="middle", legend_offset=32),
            axis_left=nivo.axis(legend="value", legend_position="middle", legend_offset=-40),
            legends=[nivo.legend(anchor="right", translate_x=100, item_width=60, symbol_shape="square")],
            on_click=log("BoxPlot"),
            height="360px",
        ),
        description="Quantiles, whiskers and subgroups.",
    )


def heatmap_card() -> rx.Component:
    return chart_card(
        "Heatmap",
        "nivo.heatmap",
        nivo.heatmap(
            data=DistributionState.heat,
            value_format=">-.0f",
            colors={
                "type": "diverging",
                "scheme": DistributionState.heat_scheme,
                "divergeAt": 0.5,
                "minValue": -100,
                "maxValue": 100,
            },
            empty_color="#555555",
            border_radius=3,
            x_inner_padding=0.04,
            y_inner_padding=0.08,
            hover_target="rowColumn",
            inactive_opacity=0.2,
            margin=nivo.margin(top=50, right=40, bottom=60, left=50),
            axis_top=nivo.axis(tick_size=5, tick_padding=5, tick_rotation=-45),
            axis_left=nivo.axis(tick_size=5, tick_padding=5),
            legends=[
                {
                    "anchor": "bottom",
                    "translateX": 0,
                    "translateY": 36,
                    "length": 360,
                    "thickness": 8,
                    "direction": "row",
                    "tickPosition": "after",
                    "tickSize": 3,
                    "tickSpacing": 4,
                    "tickOverlap": False,
                    "tickFormat": ">-.0f",
                    "title": "Value →",
                    "titleAlign": "start",
                    "titleOffset": 4,
                }
            ],
            on_click=log("HeatMap"),
            height="380px",
        ),
        control(
            "scheme",
            rx.select(
                list(nivo.DIVERGING_COLOR_SCHEMES),
                value=DistributionState.heat_scheme,
                on_change=DistributionState.set_heat_scheme,
                size="1",
            ),
        ),
        rx.button(
            rx.icon("shuffle", size=14),
            "Randomize",
            on_click=DistributionState.shuffle_heat,
            size="1",
            variant="soft",
        ),
        description="Diverging color scale, continuous legend, row/column hover.",
        code=HEATMAP_CODE,
    )


def voronoi_card() -> rx.Component:
    return chart_card(
        "Voronoi",
        "nivo.voronoi",
        nivo.voronoi(
            data=data.voronoi_data(),
            x_domain=[0, 100],
            y_domain=[0, 100],
            enable_links=DistributionState.voronoi_links,
            link_line_width=1,
            link_line_color="#cccccc",
            enable_cells=DistributionState.voronoi_cells,
            cell_line_width=1,
            cell_line_color="#6e56cf",
            point_size=6,
            point_color="#e5484d",
            margin=nivo.margin(top=10, right=10, bottom=10, left=10),
            height="360px",
        ),
        control(
            "cells",
            rx.switch(
                checked=DistributionState.voronoi_cells,
                on_change=DistributionState.set_voronoi_cells,
                size="1",
            ),
        ),
        control(
            "delaunay links",
            rx.switch(
                checked=DistributionState.voronoi_links,
                on_change=DistributionState.set_voronoi_links,
                size="1",
            ),
        ),
        description="Voronoi cells and Delaunay triangulation.",
    )


def index() -> rx.Component:
    return page(
        "Distributions",
        "How values spread: scatter, swarm, box plot, heatmap and voronoi.",
        grid(scatter_card(), swarm_card(), boxplot_card(), heatmap_card(), voronoi_card()),
    )
