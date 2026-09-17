"""Page shell, navigation and reusable cards."""

from __future__ import annotations

import reflex as rx

from .state import EventLog

NAV = [
    ("/", "Overview", "layout-dashboard"),
    ("/bars-lines", "Bars & lines", "chart-column"),
    ("/radial", "Pie & radial", "chart-pie"),
    ("/distributions", "Distributions", "chart-scatter"),
    ("/hierarchies", "Hierarchies", "network"),
    ("/flows", "Flows & relations", "waypoints"),
    ("/time", "Time", "calendar-days"),
    ("/geo", "Geo", "globe"),
    ("/canvas", "Canvas & HTML", "cpu"),
    ("/customization", "Customization", "palette"),
]


def nav_item(href: str, label: str, icon: str) -> rx.Component:
    active = rx.State.router.page.path == href
    return rx.link(
        rx.hstack(rx.icon(icon, size=16), rx.text(label, size="2"), align="center", spacing="2"),
        href=href,
        underline="none",
        padding_x="10px",
        padding_y="7px",
        border_radius="8px",
        width="100%",
        color=rx.cond(active, rx.color("accent", 11), rx.color("gray", 11)),
        background=rx.cond(active, rx.color("accent", 3), "transparent"),
        _hover={"background": rx.color("gray", 3), "color": rx.color("gray", 12)},
    )


def sidebar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.box(
                rx.icon("chart-no-axes-combined", size=18, color="white"),
                background=rx.color("accent", 9),
                border_radius="8px",
                padding="6px",
                display="flex",
            ),
            rx.vstack(
                rx.text("reflex-nivo", weight="bold", size="3"),
                rx.text("nivo for Reflex", size="1", color_scheme="gray"),
                spacing="0",
            ),
            align="center",
            spacing="3",
            margin_bottom="12px",
        ),
        *[nav_item(*item) for item in NAV],
        rx.spacer(),
        rx.hstack(
            rx.color_mode.switch(size="1"),
            rx.text("Dark mode", size="1", color_scheme="gray"),
            align="center",
            spacing="2",
        ),
        rx.link(
            rx.hstack(rx.icon("book-open", size=14), rx.text("nivo docs", size="1")),
            href="https://nivo.rocks/components/",
            is_external=True,
            color_scheme="gray",
        ),
        spacing="1",
        height="100vh",
        position="sticky",
        top="0",
        padding="18px 14px",
        width="230px",
        min_width="230px",
        border_right=f"1px solid {rx.color('gray', 4)}",
        background=rx.color("gray", 1),
        display=["none", "none", "flex"],
    )


def event_inspector() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("mouse-pointer-click", size=15),
                rx.text("Event inspector", weight="bold", size="2"),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("eraser", size=13), size="1", variant="ghost", on_click=EventLog.clear
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                EventLog.payload != "",
                rx.vstack(
                    rx.hstack(
                        rx.badge(EventLog.source, color_scheme="iris"),
                        rx.badge(EventLog.event, color_scheme="gray", variant="soft"),
                        spacing="1",
                    ),
                    rx.scroll_area(
                        rx.code_block(EventLog.payload, language="json", font_size="11px", width="100%"),
                        max_height="220px",
                        type="auto",
                        scrollbars="vertical",
                    ),
                    width="100%",
                    spacing="2",
                ),
                rx.text(
                    "Click (or hover, where enabled) any chart element: the Python handler receives the datum.",
                    size="1",
                    color_scheme="gray",
                ),
            ),
            spacing="2",
            width="100%",
        ),
        width="320px",
        position="fixed",
        bottom="16px",
        right="16px",
        z_index="10",
        box_shadow="0 8px 30px rgba(0,0,0,.12)",
        display=["none", "none", "none", "block"],
    )


def page(title: str, description: str, *children: rx.Component) -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading(title, size="7"),
                rx.text(description, color_scheme="gray", size="3"),
                *children,
                spacing="5",
                width="100%",
                max_width="1180px",
                padding=["16px", "24px", "32px"],
                padding_bottom="120px",
            ),
            width="100%",
        ),
        event_inspector(),
        spacing="0",
        align="start",
        width="100%",
        min_height="100vh",
    )


def chart_card(
    title: str,
    component: str,
    chart: rx.Component,
    *controls: rx.Component,
    description: str = "",
    code: str | None = None,
    span: int = 1,
) -> rx.Component:
    header_text = [rx.text(title, weight="bold", size="3")]
    if description:
        header_text.append(rx.text(description, size="1", color_scheme="gray"))
    body: list[rx.Component] = [
        rx.hstack(
            rx.vstack(*header_text, spacing="0"),
            rx.spacer(),
            rx.code(component, size="1", variant="soft", white_space="nowrap"),
            width="100%",
            align="start",
        )
    ]
    if controls:
        body.append(rx.flex(*controls, gap="12px", wrap="wrap", align="center", width="100%"))
    body.append(chart)
    if code:
        body.append(
            rx.accordion.root(
                rx.accordion.item(
                    header=rx.text("Python", size="1"),
                    content=rx.code_block(code.strip(), language="python", font_size="11px", width="100%"),
                    value="code",
                ),
                collapsible=True,
                variant="ghost",
                width="100%",
            )
        )
    return rx.card(
        rx.vstack(*body, spacing="3", width="100%"),
        width="100%",
        min_width="0",
        grid_column=["span 1", "span 1", f"span {span}"],
    )


def grid(*cards: rx.Component, columns: int = 2) -> rx.Component:
    return rx.grid(*cards, columns=rx.breakpoints(initial="1", md=str(columns)), gap="16px", width="100%")


def control(label: str, widget: rx.Component) -> rx.Component:
    return rx.hstack(rx.text(label, size="1", color_scheme="gray"), widget, align="center", spacing="2")
