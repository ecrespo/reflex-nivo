"""Every canvas and HTML variant, with larger datasets."""

from __future__ import annotations

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, grid, page
from ..state import log

H = "300px"
M = nivo.margin(top=20, right=20, bottom=40, left=50)


def cards() -> list[rx.Component]:
    hierarchy = data.hierarchy()
    return [
        chart_card(
            "Bar canvas · 120 groups",
            "nivo.bar_canvas",
            nivo.bar_canvas(
                data=data.bar_canvas_data(),
                keys=["a", "b", "c"],
                index_by="id",
                padding=0.15,
                colors=nivo.scheme("paired"),
                axis_bottom=None,
                enable_label=False,
                margin=M,
                on_click=log("BarCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Line canvas · 3 200 points",
            "nivo.line_canvas",
            nivo.line_canvas(
                data=data.line_canvas_data(),
                x_scale=nivo.scale("linear"),
                y_scale=nivo.scale("linear", min="auto", max="auto"),
                enable_points=False,
                line_width=1.5,
                colors=nivo.scheme("category10"),
                axis_bottom=nivo.axis(tick_values=8),
                margin=M,
                on_click=log("LineCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Scatter plot canvas · 2 000 nodes",
            "nivo.scatterplot_canvas",
            nivo.scatterplot_canvas(
                data=data.scatter_data(groups=4, points=500),
                node_size=4,
                colors=nivo.scheme("set1"),
                x_scale=nivo.scale("linear", min="auto"),
                y_scale=nivo.scale("linear", min="auto"),
                margin=M,
                on_click=log("ScatterPlotCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Swarm plot canvas",
            "nivo.swarmplot_canvas",
            nivo.swarmplot_canvas(
                data=data.swarm_data(size=300),
                groups=["group A", "group B", "group C"],
                value="price",
                size=6,
                colors=nivo.scheme("set2"),
                margin=M,
                on_click=log("SwarmPlotCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Heatmap canvas",
            "nivo.heatmap_canvas",
            nivo.heatmap_canvas(
                data=data.heatmap_data(),
                colors={"type": "sequential", "scheme": "purple_blue"},
                margin=nivo.margin(top=30, right=20, bottom=20, left=50),
                on_click=log("HeatMapCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Pie canvas",
            "nivo.pie_canvas",
            nivo.pie_canvas(
                data=data.pie_data(),
                inner_radius=0.5,
                pad_angle=1,
                corner_radius=3,
                colors=nivo.scheme("pastel1"),
                arc_link_labels_color=nivo.inherit("color"),
                margin=nivo.margin(top=30, right=80, bottom=30, left=80),
                on_click=log("PieCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Chord canvas",
            "nivo.chord_canvas",
            nivo.chord_canvas(
                data=data.chord_matrix(),
                keys=data.CHORD_KEYS,
                pad_angle=0.02,
                colors=nivo.scheme("set3"),
                margin=nivo.margin(top=40, right=40, bottom=40, left=40),
                on_arc_click=log("ChordCanvas", "on_arc_click"),
                height=H,
            ),
        ),
        chart_card(
            "Network canvas",
            "nivo.network_canvas",
            nivo.network_canvas(
                data=data.network_data(seed=5),
                node_color=nivo.js("(n) => n.color"),
                node_size=nivo.js("(n) => n.size"),
                link_distance=nivo.js("(l) => l.distance"),
                repulsivity=6,
                on_click=log("NetworkCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Parallel coordinates canvas",
            "nivo.parallel_coordinates_canvas",
            nivo.parallel_coordinates_canvas(
                data=data.parallel_data(size=200),
                variables=data.PARALLEL_VARIABLES,
                group_by="kind",
                colors=nivo.scheme("set1"),
                line_opacity=0.25,
                margin=nivo.margin(top=40, right=30, bottom=20, left=50),
                height=H,
            ),
        ),
        chart_card(
            "Tree canvas",
            "nivo.tree_canvas",
            nivo.tree_canvas(
                data=hierarchy,
                identity="name",
                layout="left-to-right",
                node_size=8,
                link_thickness=1.5,
                node_color=nivo.scheme("category10"),
                margin=nivo.margin(top=10, right=90, bottom=10, left=90),
                on_node_click=log("TreeCanvas", "on_node_click"),
                height=H,
            ),
        ),
        chart_card(
            "Treemap canvas",
            "nivo.treemap_canvas",
            nivo.treemap_canvas(
                data=hierarchy,
                identity="name",
                value="loc",
                colors=nivo.scheme("set2"),
                inner_padding=1,
                label_skip_size=18,
                on_click=log("TreeMapCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Treemap HTML",
            "nivo.treemap_html",
            nivo.treemap_html(
                data=hierarchy,
                identity="name",
                value="loc",
                colors=nivo.scheme("pastel2"),
                outer_padding=4,
                label_skip_size=24,
                on_click=log("TreeMapHtml"),
                height=H,
            ),
        ),
        chart_card(
            "Circle packing canvas",
            "nivo.circle_packing_canvas",
            nivo.circle_packing_canvas(
                data=hierarchy,
                id_by="name",
                value="loc",
                padding=2,
                colors=nivo.scheme("yellow_green_blue"),
                color_by="depth",
                on_click=log("CirclePackingCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Circle packing HTML",
            "nivo.circle_packing_html",
            nivo.circle_packing_html(
                data=hierarchy,
                id_by="name",
                value="loc",
                padding=3,
                enable_labels=True,
                leaves_only=True,
                labels_skip_radius=16,
                colors=nivo.scheme("nivo"),
                on_click=log("CirclePackingHtml"),
                height=H,
            ),
        ),
        chart_card(
            "Icicle HTML",
            "nivo.icicle_html",
            nivo.icicle_html(
                data=hierarchy,
                identity="name",
                value="loc",
                orientation="bottom",
                enable_labels=True,
                label_skip_width=30,
                colors=nivo.scheme("tableau10"),
                inherit_color_from_parent=True,
                enable_zooming=True,
                on_click=log("IcicleHtml"),
                height=H,
            ),
        ),
        chart_card(
            "Waffle canvas · 2 500 cells",
            "nivo.waffle_canvas",
            nivo.waffle_canvas(
                data=data.waffle_data(),
                total=100,
                rows=50,
                columns=50,
                padding=1,
                colors=nivo.scheme("category10"),
                on_click=log("WaffleCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "Waffle HTML",
            "nivo.waffle_html",
            nivo.waffle_html(
                data=data.waffle_data(),
                total=100,
                rows=10,
                columns=20,
                padding=2,
                colors=nivo.scheme("set2"),
                border_radius=4,
                on_click=log("WaffleHtml"),
                height=H,
            ),
        ),
        chart_card(
            "Calendar canvas",
            "nivo.calendar_canvas",
            nivo.calendar_canvas(
                data=data.calendar_data(),
                from_date="2025-01-01",
                to_date="2025-12-31",
                empty_color=rx.color_mode_cond("#ebedf0", "#26282c"),
                colors=["#9be9a8", "#40c463", "#30a14e", "#216e39"],
                margin=nivo.margin(top=30, right=20, bottom=10, left=30),
                on_click=log("CalendarCanvas"),
                height=H,
            ),
        ),
        chart_card(
            "GeoMap canvas",
            "nivo.geo_map_canvas",
            nivo.geo_map_canvas(
                features=data.world_features(),
                projection_type="mercator",
                projection_scale=70,
                projection_translation=[0.5, 0.65],
                fill_color="#8e9cf2",
                border_width=0.4,
                border_color="#1e2a78",
                on_click=log("GeoMapCanvas"),
                height=H,
            ),
        ),
    ]


def index() -> rx.Component:
    return page(
        "Canvas & HTML",
        "Canvas variants keep thousands of marks smooth; HTML variants render plain DOM nodes. Same props, different renderer.",
        grid(*cards(), columns=2),
    )
