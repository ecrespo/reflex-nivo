"""Landing page."""

from __future__ import annotations

import reflex as rx
import reflex_nivo as nivo

from .. import data
from ..layout import NAV, page

QUICKSTART = """
import reflex as rx
import reflex_nivo as nivo


class State(rx.State):
    rows: list[dict] = [
        {"country": "AD", "burger": 120, "fries": 80},
        {"country": "AE", "burger": 95, "fries": 130},
    ]
    selected: str = ""

    @rx.event
    def on_bar_click(self, datum: dict):
        self.selected = f"{datum['indexValue']} · {datum['id']} = {datum['value']}"


def index():
    return rx.vstack(
        nivo.bar(
            data=State.rows,
            keys=["burger", "fries"],
            index_by="country",
            colors=nivo.scheme("nivo"),
            axis_bottom=nivo.axis(legend="country", legend_offset=32),
            on_click=State.on_bar_click,
            height="400px",          # container size (nivo charts fill their parent)
        ),
        rx.text(State.selected),
    )
"""

STATS = [
    ("51", "components"),
    ("28", "nivo packages"),
    ("3", "renderers: SVG · Canvas · HTML"),
    ("0.99", "nivo version"),
]


def mini(title: str, chart: rx.Component, href: str) -> rx.Component:
    return rx.link(
        rx.card(
            rx.vstack(chart, rx.text(title, size="2", weight="medium"), spacing="1", width="100%"),
            width="100%",
            _hover={"box_shadow": "0 6px 24px rgba(0,0,0,.10)", "transform": "translateY(-2px)"},
            transition="all .15s ease",
        ),
        href=href,
        underline="none",
        color="inherit",
        width="100%",
    )


def gallery() -> rx.Component:
    none = {"is_interactive": False, "height": "150px"}
    tight = nivo.margin(top=6, right=6, bottom=6, left=6)
    return rx.grid(
        mini(
            "Bar",
            nivo.bar(
                data=data.bar_data(),
                keys=data.FOODS[:3],
                index_by="country",
                enable_label=False,
                axis_bottom=None,
                axis_left=None,
                enable_grid_y=False,
                margin=tight,
                padding=0.2,
                **none,
            ),
            "/bars-lines",
        ),
        mini(
            "Line",
            nivo.line(
                data=data.line_data()[:3],
                enable_points=False,
                axis_bottom=None,
                axis_left=None,
                enable_grid_x=False,
                enable_grid_y=False,
                curve="monotoneX",
                margin=tight,
                line_width=3,
                **none,
            ),
            "/bars-lines",
        ),
        mini(
            "Pie",
            nivo.pie(
                data=data.pie_data(),
                inner_radius=0.55,
                pad_angle=2,
                corner_radius=3,
                enable_arc_link_labels=False,
                enable_arc_labels=False,
                margin=tight,
                **none,
            ),
            "/radial",
        ),
        mini(
            "Sunburst",
            nivo.sunburst(
                data=data.hierarchy(),
                id_by="name",
                value="loc",
                enable_arc_labels=False,
                margin=tight,
                child_color=nivo.inherit("color", ("brighter", 0.3)),
                **none,
            ),
            "/hierarchies",
        ),
        mini(
            "Chord",
            nivo.chord(
                data=data.chord_matrix(), keys=data.CHORD_KEYS, enable_label=False, margin=tight, **none
            ),
            "/flows",
        ),
        mini(
            "Heatmap",
            nivo.heatmap(
                data=data.heatmap_data(),
                enable_labels=False,
                axis_top=None,
                axis_left=None,
                colors={"type": "diverging", "scheme": "red_yellow_blue"},
                margin=tight,
                **none,
            ),
            "/distributions",
        ),
        mini(
            "Stream",
            nivo.stream(
                data=data.stream_data(),
                keys=["Raoul", "Josiane", "Marcel", "René"],
                axis_bottom=None,
                axis_left=None,
                enable_grid_x=False,
                enable_grid_y=False,
                margin=tight,
                **none,
            ),
            "/time",
        ),
        mini(
            "Choropleth",
            nivo.choropleth(
                features=data.world_features(),
                data=data.choropleth_data(),
                domain=[0, 1_000_000],
                colors="blues",
                projection_scale=38,
                projection_translation=[0.5, 0.62],
                margin=nivo.margin(),
                **none,
            ),
            "/geo",
        ),
        columns=rx.breakpoints(initial="2", md="4"),
        gap="12px",
        width="100%",
    )


def index() -> rx.Component:
    return page(
        "nivo, in pure Python",
        "reflex-nivo wraps every chart of nivo — the React dataviz library built on d3 — as a typed Reflex component. "
        "Props are snake_case, data comes from state, and clicks land in your event handlers.",
        rx.hstack(
            rx.code("pip install reflex-nivo", size="3", variant="soft", padding="8px 12px"),
            rx.link(
                rx.button(rx.icon("git-branch", size=14), "nivo on GitHub", variant="outline", size="2"),
                href="https://github.com/plouc/nivo",
                is_external=True,
            ),
            rx.link(
                rx.button(rx.icon("book-open", size=14), "nivo.rocks", variant="outline", size="2"),
                href="https://nivo.rocks/components/",
                is_external=True,
            ),
            spacing="3",
            wrap="wrap",
            align="center",
        ),
        rx.grid(
            *[
                rx.card(
                    rx.vstack(
                        rx.text(value, size="7", weight="bold"),
                        rx.text(label, size="1", color_scheme="gray"),
                        spacing="0",
                    )
                )
                for value, label in STATS
            ],
            columns=rx.breakpoints(initial="2", md="4"),
            gap="12px",
            width="100%",
        ),
        gallery(),
        rx.heading("Quick start", size="5"),
        rx.code_block(
            QUICKSTART.strip(), language="python", show_line_numbers=True, width="100%", font_size="12px"
        ),
        rx.heading("Explore", size="5"),
        rx.grid(
            *[
                rx.link(
                    rx.card(
                        rx.hstack(
                            rx.icon(icon, size=18),
                            rx.text(label, weight="medium"),
                            align="center",
                            spacing="2",
                        )
                    ),
                    href=href,
                    underline="none",
                    color="inherit",
                )
                for href, label, icon in NAV[1:]
            ],
            columns=rx.breakpoints(initial="1", sm="2", md="3"),
            gap="12px",
            width="100%",
        ),
    )
