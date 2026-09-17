"""Treemap, sunburst, circle packing, icicle and tree."""

from __future__ import annotations

from typing import Any

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import chart_card, control, grid, page
from ..state import EventLog, log


class HierarchyState(rx.State):
    tile: str = "squarify"
    sunburst: dict[str, Any] = data.hierarchy()
    sunburst_path: list[str] = ["reflex-app"]
    zoomed_id: str = ""
    tree_layout: str = "top-to-bottom"
    tree_mode: str = "tree"

    @rx.event
    def set_tile(self, value: str):
        self.tile = value

    @rx.event
    def set_tree_layout(self, value: str):
        self.tree_layout = value

    @rx.event
    def set_tree_mode(self, value: str | list[str]):
        self.tree_mode = str(value)

    @rx.event
    def drill_down(self, node: dict[str, Any]):
        """Replace the sunburst data with the clicked branch."""
        branch = node.get("data") or {}
        if branch.get("children"):
            self.sunburst = branch
            self.sunburst_path = [*self.sunburst_path, str(branch.get("name"))]
        return EventLog.record("Sunburst", "on_click", node)

    @rx.event
    def reset_sunburst(self):
        self.sunburst = data.hierarchy()
        self.sunburst_path = ["reflex-app"]

    @rx.event
    def zoom(self, node: dict[str, Any]):
        """Toggle circle packing zoom on the clicked circle."""
        node_id = str(node.get("id", ""))
        self.zoomed_id = "" if node_id == self.zoomed_id else node_id

    @rx.var
    def breadcrumb(self) -> str:
        return " / ".join(self.sunburst_path)


SUNBURST_CODE = """
class State(rx.State):
    sunburst: dict = data.hierarchy()

    @rx.event
    def drill_down(self, node: dict):
        branch = node.get("data") or {}   # the raw datum is included in the event
        if branch.get("children"):
            self.sunburst = branch

nivo.sunburst(
    data=State.sunburst,
    id_by="name",                          # nivo's `id` prop
    value="loc",
    corner_radius=2,
    child_color=nivo.inherit("color", ("brighter", 0.3)),
    on_click=State.drill_down,
)
"""


def treemap_card() -> rx.Component:
    return chart_card(
        "Treemap",
        "nivo.treemap",
        nivo.treemap(
            data=data.hierarchy(),
            identity="name",
            value="loc",
            value_format=".02s",
            tile=HierarchyState.tile,
            label_skip_size=16,
            label=nivo.template("{id}"),
            label_text_color=nivo.inherit("color", ("darker", 2.2)),
            parent_label_position="left",
            parent_label_text_color=nivo.inherit("color", ("darker", 2.5)),
            border_color=nivo.inherit("color", ("darker", 0.15)),
            colors=nivo.scheme("tableau10"),
            node_opacity=0.9,
            margin=nivo.margin(top=6, right=6, bottom=6, left=6),
            on_click=log("TreeMap"),
            height="400px",
        ),
        control(
            "tile",
            rx.select(
                ["squarify", "binary", "dice", "slice", "sliceDice"],
                value=HierarchyState.tile,
                on_change=HierarchyState.set_tile,
                size="1",
            ),
        ),
        description="Tiling algorithms, parent labels, template labels.",
        span=2,
    )


def sunburst_card() -> rx.Component:
    return chart_card(
        "Sunburst with drill-down",
        "nivo.sunburst",
        nivo.sunburst(
            data=HierarchyState.sunburst,
            id_by="name",
            value="loc",
            corner_radius=2,
            border_width=1,
            border_color=nivo.from_theme("background"),
            colors=nivo.scheme("nivo"),
            child_color=nivo.inherit("color", ("brighter", 0.3)),
            enable_arc_labels=True,
            arc_labels_skip_angle=12,
            arc_labels_text_color=nivo.inherit("color", ("darker", 1.4)),
            tooltip=nivo.tooltip("<b>{id}</b>: {formattedValue} LOC ({percentage}%)"),
            value_format=".3s",
            margin=nivo.margin(top=10, right=10, bottom=10, left=10),
            on_click=HierarchyState.drill_down,
            height="380px",
        ),
        rx.badge(HierarchyState.breadcrumb, variant="soft"),
        rx.button(
            rx.icon("undo-2", size=14),
            "Reset",
            on_click=HierarchyState.reset_sunburst,
            size="1",
            variant="soft",
        ),
        description="Click a branch: the Python handler swaps the data for that subtree.",
        code=SUNBURST_CODE,
    )


def circle_packing_card() -> rx.Component:
    return chart_card(
        "Circle packing with zoom",
        "nivo.circle_packing",
        nivo.circle_packing(
            data=data.hierarchy(),
            id_by="name",
            value="loc",
            zoomed_id=rx.cond(HierarchyState.zoomed_id != "", HierarchyState.zoomed_id, None),
            padding=4,
            enable_labels=True,
            labels_filter=nivo.js("(label) => label.node.height === 0"),
            labels_skip_radius=12,
            label_text_color=nivo.inherit("color", ("darker", 2)),
            colors=nivo.scheme("spectral"),
            child_color=nivo.inherit("color", ("brighter", 0.4)),
            border_width=1,
            border_color=nivo.inherit("color", ("darker", 0.5)),
            motion_config="slow",
            margin=nivo.margin(top=10, right=10, bottom=10, left=10),
            on_click=HierarchyState.zoom,
            height="380px",
        ),
        rx.badge(
            "zoomed: ",
            rx.cond(HierarchyState.zoomed_id != "", HierarchyState.zoomed_id, "—"),
            variant="outline",
        ),
        description="zoomed_id bound to state; a JS labels_filter shows leaf labels only.",
    )


def icicle_card() -> rx.Component:
    return chart_card(
        "Icicle",
        "nivo.icicle",
        nivo.icicle(
            data=data.hierarchy(),
            identity="name",
            value="loc",
            orientation="right",
            gap_x=2,
            gap_y=2,
            border_radius=3,
            enable_zooming=True,
            enable_labels=True,
            label_skip_width=40,
            label_skip_height=14,
            label_text_color=nivo.inherit("color", ("darker", 2.4)),
            colors=nivo.scheme("paired"),
            inherit_color_from_parent=True,
            child_color=nivo.inherit("color", ("brighter", 0.2)),
            margin=nivo.margin(top=4, right=4, bottom=4, left=4),
            on_click=log("Icicle"),
            height="380px",
        ),
        description="Partition layout with built-in click-to-zoom.",
    )


def tree_card() -> rx.Component:
    return chart_card(
        "Tree / dendrogram",
        "nivo.tree",
        nivo.tree(
            data=data.hierarchy(),
            identity="name",
            mode=HierarchyState.tree_mode,
            layout=HierarchyState.tree_layout,
            node_size=12,
            active_node_size=22,
            inactive_node_size=10,
            node_color=nivo.scheme("tableau10"),
            fix_node_color_at_depth=1,
            link_thickness=2,
            active_link_thickness=6,
            inactive_link_thickness=2,
            link_color=nivo.inherit("target.color", ("opacity", 0.25)),
            label_offset=8,
            orient_label=True,
            highlight_ancestor_nodes=True,
            highlight_ancestor_links=True,
            use_mesh=True,
            margin=nivo.margin(top=70, right=40, bottom=90, left=40),
            motion_config="stiff",
            on_node_click=log("Tree", "on_node_click"),
            height="440px",
        ),
        control(
            "mode",
            rx.segmented_control.root(
                rx.segmented_control.item("tree", value="tree"),
                rx.segmented_control.item("dendogram", value="dendogram"),
                value=HierarchyState.tree_mode,
                on_change=HierarchyState.set_tree_mode,
                size="1",
            ),
        ),
        control(
            "layout",
            rx.select(
                ["top-to-bottom", "bottom-to-top", "left-to-right", "right-to-left"],
                value=HierarchyState.tree_layout,
                on_change=HierarchyState.set_tree_layout,
                size="1",
            ),
        ),
        description="Highlights ancestors on hover; on_node_click event.",
        span=2,
    )


def index() -> rx.Component:
    return page(
        "Hierarchies",
        "Nested data rendered five ways, including state-driven drill-down and zoom.",
        grid(treemap_card(), sunburst_card(), circle_packing_card(), icicle_card(), tree_card()),
    )
