"""Generate the Reflex wrappers for every nivo chart.

Reads ``nivo_props.json`` (produced by ``extract_nivo_props.cjs`` from nivo's
TypeScript declarations) plus ``nivo_manual_props.json`` (packages without
usable typings) and writes one module per nivo package into
``custom_components/reflex_nivo/charts/``.

Run from the repository root:

    python scripts/generate_components.py
"""

from __future__ import annotations

import json
import keyword
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "custom_components" / "reflex_nivo" / "charts"

# npm package -> python module name.
PACKAGES: dict[str, str] = {
    "area-bump": "bump",  # AreaBump lives in @nivo/bump (handled via EXPORT_PACKAGE)
}

# Python factory names for classes whose snake_case would be awkward.
FACTORY_NAMES: dict[str, str] = {
    "HeatMap": "heatmap",
    "HeatMapCanvas": "heatmap_canvas",
    "ScatterPlot": "scatterplot",
    "ScatterPlotCanvas": "scatterplot_canvas",
    "SwarmPlot": "swarmplot",
    "SwarmPlotCanvas": "swarmplot_canvas",
    "TreeMap": "treemap",
    "TreeMapHtml": "treemap_html",
    "TreeMapCanvas": "treemap_canvas",
    "BoxPlot": "boxplot",
}

DESCRIPTIONS: dict[str, str] = {
    "AreaBump": "Area bump chart: ranking evolution with areas proportional to values.",
    "Bar": "Bar chart (grouped/stacked, vertical/horizontal).",
    "BarCanvas": "Bar chart rendered on canvas, for large datasets.",
    "BoxPlot": "Box plot showing distributions (quantiles, whiskers, outliers).",
    "Bullet": "Bullet charts comparing a measure against ranges and markers.",
    "Bump": "Bump chart: ranking evolution over time.",
    "Calendar": "Calendar heatmap of daily values across years.",
    "CalendarCanvas": "Calendar heatmap rendered on canvas.",
    "Choropleth": "Choropleth map: GeoJSON features colored by value.",
    "ChoroplethCanvas": "Choropleth map rendered on canvas.",
    "Chord": "Chord diagram of flows between groups (square matrix).",
    "ChordCanvas": "Chord diagram rendered on canvas.",
    "CirclePacking": "Circle packing of hierarchical data.",
    "CirclePackingCanvas": "Circle packing rendered on canvas.",
    "CirclePackingHtml": "Circle packing rendered with HTML elements.",
    "Funnel": "Funnel chart for sequential conversion steps.",
    "GeoMap": "Geographic map of GeoJSON features.",
    "GeoMapCanvas": "Geographic map rendered on canvas.",
    "HeatMap": "Heatmap of a matrix of values.",
    "HeatMapCanvas": "Heatmap rendered on canvas.",
    "Icicle": "Icicle (partition) chart of hierarchical data.",
    "IcicleHtml": "Icicle chart rendered with HTML elements.",
    "Line": "Line/area chart with linear, point, log or time scales.",
    "LineCanvas": "Line chart rendered on canvas.",
    "Marimekko": "Marimekko (mosaic) chart: variable-width stacked bars.",
    "Network": "Force-directed network graph.",
    "NetworkCanvas": "Force-directed network graph rendered on canvas.",
    "ParallelCoordinates": "Parallel coordinates for multivariate data.",
    "ParallelCoordinatesCanvas": "Parallel coordinates rendered on canvas.",
    "Pie": "Pie / donut chart.",
    "PieCanvas": "Pie / donut chart rendered on canvas.",
    "PolarBar": "Polar bar chart (stacked arcs around a circle).",
    "Radar": "Radar (spider) chart.",
    "RadialBar": "Radial bar chart.",
    "Sankey": "Sankey diagram of flows between nodes.",
    "ScatterPlot": "Scatter plot of x/y series.",
    "ScatterPlotCanvas": "Scatter plot rendered on canvas.",
    "Stream": "Stream graph (stacked areas around a baseline).",
    "Sunburst": "Sunburst of hierarchical data.",
    "SwarmPlot": "Swarm plot (beeswarm) of values grouped by category.",
    "SwarmPlotCanvas": "Swarm plot rendered on canvas.",
    "TimeRange": "Calendar-like heatmap over an arbitrary date range.",
    "Tree": "Tree / dendrogram layout of hierarchical data.",
    "TreeCanvas": "Tree layout rendered on canvas.",
    "TreeMap": "Treemap of hierarchical data.",
    "TreeMapCanvas": "Treemap rendered on canvas.",
    "TreeMapHtml": "Treemap rendered with HTML elements.",
    "Voronoi": "Voronoi tessellation of points.",
    "Waffle": "Waffle chart of proportions on a grid.",
    "WaffleCanvas": "Waffle chart rendered on canvas.",
    "WaffleHtml": "Waffle chart rendered with HTML elements.",
}

# Short docs for props that appear on many charts.
PROP_DOCS: dict[str, str] = {
    "data": "Chart data (see the nivo docs of this chart for the expected shape).",
    "margin": "Chart margin: {'top': .., 'right': .., 'bottom': .., 'left': ..}.",
    "colors": "Colors: {'scheme': 'nivo'}, a list of colors, a color, or a JS function.",
    "theme": "nivo theme; defaults to reflex_nivo.themes.auto() (follows color mode).",
    "animate": "Enable/disable transitions.",
    "motionConfig": "react-spring preset ('gentle', 'wobbly', ...) or a config dict.",
    "isInteractive": "Enable tooltips and mouse events.",
    "tooltip": "Tooltip component: use reflex_nivo.tooltip('{template}') or reflex_nivo.js(...).",
    "legends": "Legends configuration (see reflex_nivo.legend()).",
    "layers": "Layers to render, in order (strings or custom JS layers).",
    "valueFormat": "d3-format specifier (e.g. ' >-.2f') or JS function.",
    "defs": "SVG pattern/gradient definitions (see reflex_nivo.pattern_dots_def & co).",
    "fill": "Rules matching data to defs: [{'match': {'id': 'x'}, 'id': 'dots'}].",
    "role": "ARIA role of the chart root.",
    "renderWrapper": "Render the wrapping div nivo uses for tooltips.",
    "defaultWidth": "Width used before the container has been measured.",
    "defaultHeight": "Height used before the container has been measured.",
    "debounceResize": "Debounce (ms) applied to container resize detection.",
    "pixelRatio": "Canvas pixel ratio (defaults to window.devicePixelRatio).",
    "axisTop": "Top axis config dict, or None to hide (see reflex_nivo.axis()).",
    "axisRight": "Right axis config dict, or None to hide (see reflex_nivo.axis()).",
    "axisBottom": "Bottom axis config dict, or None to hide (see reflex_nivo.axis()).",
    "axisLeft": "Left axis config dict, or None to hide (see reflex_nivo.axis()).",
    "xScale": "x scale spec, e.g. {'type': 'linear', 'min': 'auto'}.",
    "yScale": "y scale spec, e.g. {'type': 'linear', 'stacked': True}.",
    "idBy": "Accessor for the datum id (nivo's `id` prop): a key name or JS function.",
    "fromDate": "Start date (nivo's `from` prop), 'YYYY-MM-DD'.",
    "toDate": "End date (nivo's `to` prop), 'YYYY-MM-DD'.",
    "annotations": "Annotations: [{'type': 'circle', 'match': {...}, 'note': '...'}].",
    "markers": "Cartesian markers: [{'axis': 'y', 'value': 0, 'legend': '...'}].",
}

# Defaults injected by the wrapper to work around missing defaults upstream.
DEFAULT_PROPS: dict[str, dict] = {
    # nivo 0.99 GeoMapCanvas crashes when `layers` is not provided.
    "GeoMapCanvas": {"layers": ["graticule", "features"]},
}

# Props never exposed.
SKIP = {"ref", "key", "children", "width", "height", "style"}

# nivo prop -> python-safe camelCase name (mirrored by NivoComponent._rename_props).
RENAME = {"id": "idBy", "from": "fromDate", "to": "toDate"}

NAMED_TYPES = {
    "string": "str",
    "number": "int | float",
    "boolean": "bool",
    "true": "bool",
    "false": "bool",
    "DatumId": "str | int | float",
    "CssMixBlendMode": "str",
    "BoxAlign": "str",
    "LineCurveFactoryId": "str",
    "AreaCurve": "str",
    "CrosshairType": "str",
    "string[]": "Sequence[str]",
    "readonly string[]": "Sequence[str]",
    "number[]": "Sequence[int | float]",
    "readonly number[]": "Sequence[int | float]",
    "[number, number]": "Sequence[int | float]",
    "[number, number, number]": "Sequence[int | float]",
}


def split_union(text: str) -> list[str]:
    """Split a TS union at top level."""
    parts, depth, current = [], 0, ""
    for char in text:
        if char in "<({[":
            depth += 1
        elif char in ">)}]":
            depth -= 1
        if char == "|" and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    parts.append(current.strip())
    return [p for p in parts if p]


def strip_parens(text: str) -> str:
    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth = 0
        for i, char in enumerate(text):
            depth += char == "("
            depth -= char == ")"
            if depth == 0 and i < len(text) - 1:
                return text
        text = text[1:-1].strip()
    return text


def map_type(ts_type: str) -> str:
    """Map a TypeScript type to a Python annotation for rx.Var[...]."""
    parts = [strip_parens(p) for p in split_union(ts_type)]
    nullable = "null" in parts
    parts = [p for p in parts if p not in ("undefined", "null")]
    if not parts or any("=>" in p for p in parts):
        return "Any"
    literals: list[str] = []
    mapped: list[str] = []
    for part in parts:
        if re.fullmatch(r'"[^"]*"', part):
            literals.append(part)
        elif part in NAMED_TYPES:
            mapped.append(NAMED_TYPES[part])
        else:
            return "Any"
    pieces: list[str] = []
    if literals and "str" not in mapped:
        pieces.append(f"Literal[{', '.join(literals)}]")
    for item in mapped:
        for sub in item.split(" | ") if not item.startswith("Sequence") else [item]:
            if sub not in pieces:
                pieces.append(sub)
    if nullable:
        pieces.append("None")
    return " | ".join(pieces)


def snake(name: str) -> str:
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return name.lower()


def to_camel(name: str) -> str:
    head, *rest = name.split("_")
    return head + "".join(word.capitalize() for word in rest)


DOC_SLUGS = {
    "HeatMap": "heatmap",
    "ScatterPlot": "scatterplot",
    "SwarmPlot": "swarmplot",
    "TreeMap": "treemap",
    "BoxPlot": "boxplot",
    "GeoMap": "geomap",
}


def docs_url(class_name: str) -> str:
    base = re.sub(r"(Canvas|Html)$", "", class_name)
    slug = DOC_SLUGS.get(base, snake(base).replace("_", "-"))
    suffix = {"canvas": "canvas/", "html": "html/"}.get(variant_of(class_name), "")
    return f"https://nivo.rocks/{slug}/{suffix}"


def variant_of(class_name: str) -> str:
    if class_name.endswith("Canvas"):
        return "canvas"
    if class_name.endswith("Html"):
        return "html"
    return "svg"


def parse_prop(entry: str) -> tuple[str, bool, str]:
    name, _, ts_type = entry.partition(":")
    optional = name.endswith("?")
    return name.rstrip("?").strip(), optional, ts_type.strip()


def main() -> None:
    specs = json.loads((ROOT / "scripts" / "nivo_props.json").read_text())
    specs.update(json.loads((ROOT / "scripts" / "nivo_manual_props.json").read_text()))

    by_package: dict[str, list[tuple[str, list[str]]]] = {}
    for key, props in specs.items():
        package, export = key.split(":")
        by_package.setdefault(package, []).append((export, props))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_exports: list[tuple[str, str, str]] = []  # (module, class, factory)

    for package in sorted(by_package):
        module = package.replace("-", "_")
        lines = [
            f'"""Reflex wrappers for @nivo/{package}.',
            "",
            "Generated by scripts/generate_components.py -- do not edit by hand.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "from collections.abc import Sequence",
            "from typing import Any, ClassVar, Literal",
            "",
            "from reflex.event import EventHandler",
            "from reflex.vars.base import Var",
            "",
            "from ..base import NivoComponent, nivo_event_spec",
            "from ..constants import nivo_package",
            "",
        ]
        factories: list[tuple[str, str]] = []
        for export, props in sorted(by_package[package]):
            class_name = export.removeprefix("Responsive")
            factory = FACTORY_NAMES.get(class_name, snake(class_name))
            variant = variant_of(class_name)
            lines += [
                "",
                f"class {class_name}(NivoComponent):",
                f'    """{DESCRIPTIONS.get(class_name, class_name)}',
                "",
                f"    Wraps ``{export}`` from ``@nivo/{package}``.",
                f"    Docs: {docs_url(class_name)}",
                '    """',
                "",
                f'    library = nivo_package("{package}")',
                f'    tag = "{export}"',
                f'    _nivo_variant: ClassVar[str] = "{variant}"',
            ]
            if class_name in DEFAULT_PROPS:
                lines.append(f"    _default_props: ClassVar[dict[str, Any]] = {DEFAULT_PROPS[class_name]!r}")
            lines.append("")
            seen: set[str] = set()
            events: list[str] = []
            for entry in sorted(props, key=lambda e: parse_prop(e)[0]):
                name, optional, ts_type = parse_prop(entry)
                if name in SKIP or name in seen:
                    continue
                seen.add(name)
                py_camel = RENAME.get(name, name)
                attr = snake(py_camel)
                if to_camel(attr) != py_camel or keyword.iskeyword(attr):
                    raise SystemExit(f"cannot map prop {name!r} of {export}")
                if re.fullmatch(r"on[A-Z]\w*", name):
                    events.append(f"    {attr}: EventHandler[nivo_event_spec]")
                    continue
                doc = PROP_DOCS.get(py_camel)
                required = "" if optional else " (required)"
                comment = doc or f"TS: {ts_type[:110]}"
                lines.append(f"    # {comment}{required}")
                lines.append(f"    {attr}: Var[{map_type(ts_type)}]")
            if events:
                lines += ["", "    # Events: the handler receives the JSON-safe first callback argument."]
                lines += events
            lines.append("")
            factories.append((factory, class_name))
            all_exports.append((module, class_name, factory))
        lines.append("")
        for factory, class_name in factories:
            lines.append(f"{factory} = {class_name}.create")
        names = sorted([c for _, c in factories] + [f for f, _ in factories])
        lines += ["", "__all__ = ["] + [f'    "{n}",' for n in names] + ["]", ""]
        (OUT_DIR / f"{module}.py").write_text("\n".join(lines))

    init = ['"""All nivo chart wrappers (generated)."""', "", "from __future__ import annotations", ""]
    for module, class_name, factory in sorted(all_exports):
        init.append(f"from .{module} import {class_name}, {factory}")
    init += ["", "__all__ = ["]
    init += [f'    "{n}",' for n in sorted({x for _, c, f in all_exports for x in (c, f)})]
    init += ["]", ""]
    (OUT_DIR / "__init__.py").write_text("\n".join(init))
    print(f"generated {len(all_exports)} components in {len(by_package)} modules")


if __name__ == "__main__":
    main()
