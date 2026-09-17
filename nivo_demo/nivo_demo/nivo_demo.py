"""reflex-nivo demo app: every nivo chart wrapped as a Reflex component."""

import reflex as rx

from .pages import (
    bars_lines,
    canvas,
    customization,
    distributions,
    flows,
    geo,
    hierarchies,
    overview,
    radial,
    time,
)

app = rx.App()

PAGES = [
    (overview.index, "/", "Overview"),
    (bars_lines.index, "/bars-lines", "Bars & lines"),
    (radial.index, "/radial", "Pie & radial"),
    (distributions.index, "/distributions", "Distributions"),
    (hierarchies.index, "/hierarchies", "Hierarchies"),
    (flows.index, "/flows", "Flows & relations"),
    (time.index, "/time", "Time"),
    (geo.index, "/geo", "Geo"),
    (canvas.index, "/canvas", "Canvas & HTML"),
    (customization.index, "/customization", "Customization"),
]

for component, route, title in PAGES:
    app.add_page(component, route=route, title=f"{title} · reflex-nivo")
