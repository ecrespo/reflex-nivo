"""Pythonic helpers to build nivo prop values.

nivo props are plain JS objects with camelCase keys. These helpers accept
snake_case keyword arguments (which may be Reflex Vars) and return the dict
nivo expects, plus a few wrappers to pass JavaScript where nivo accepts
functions (formatters, labels, tooltips, custom layers).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from reflex.vars.base import Var
from reflex.vars.function import FunctionStringVar

from .constants import LegendAnchor, LegendDirection, LegendSymbolShape


# --------------------------------------------------------------------------- #
# Generic
# --------------------------------------------------------------------------- #
def _camel(name: str) -> str:
    name = name.rstrip("_")  # allow from_=..., type_=...
    head, *rest = name.split("_")
    return head + "".join(word[:1].upper() + word[1:] for word in rest)


def camelize(value: Any) -> Any:
    """Recursively convert snake_case dict keys to camelCase.

    Args:
        value: A dict/list structure (Vars are left untouched).

    Returns:
        The same structure with camelCase keys.
    """
    if isinstance(value, Var):
        return value
    if isinstance(value, Mapping):
        return {_camel(str(k)): camelize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [camelize(v) for v in value]
    return value


def props(**kwargs: Any) -> dict[str, Any]:
    """Build any nivo config object from snake_case keyword arguments.

    ``None`` values are dropped.

    Example:
        ``nivo.props(tick_size=5, tick_rotation=-45)`` ->
        ``{"tickSize": 5, "tickRotation": -45}``

    Args:
        **kwargs: The config keys.

    Returns:
        A camelCase dict.
    """
    return camelize({k: v for k, v in kwargs.items() if v is not None})


# --------------------------------------------------------------------------- #
# JavaScript escape hatches
# --------------------------------------------------------------------------- #
def js(code: str) -> Var:
    """Pass a raw JavaScript expression as a prop value.

    Use it for props nivo accepts as functions, e.g.
    ``value_format=nivo.js("v => `${v} €`")`` or custom layers.

    The code runs in the browser; never build it from untrusted input.

    Args:
        code: A JS expression.

    Returns:
        A Var rendering the expression verbatim.
    """
    return Var(_js_expr=f"({code})", _var_type=Any)


def template(text: str | Var[str]) -> Var:
    """A formatter function built from a ``{path}`` template.

    Placeholders are dotted paths read from the object nivo passes to the
    function, e.g. ``label=nivo.template("{id}: {formattedValue}")`` or
    ``axis(format=nivo.template("{}"))``. For primitive arguments (axis ticks)
    use ``nivo.js("v => ...")`` instead.

    Args:
        text: The template string (may be a Var).

    Returns:
        A Var holding a JS function ``(datum) => string``.
    """
    return FunctionStringVar.create("reflexNivoTemplate").call(text)


def tooltip(text: str | Var[str], style: Mapping[str, Any] | None = None) -> Var:
    """A tooltip component built from an HTML ``{path}`` template.

    The props nivo passes to the tooltip differ per chart, e.g.:

    - Bar: ``{id}``, ``{value}``, ``{formattedValue}``, ``{indexValue}``, ``{color}``, ``{data.<key>}``
    - Pie: ``{datum.id}``, ``{datum.formattedValue}``, ``{datum.color}``
    - Line: ``{point.seriesId}``, ``{point.data.xFormatted}``, ``{point.data.yFormatted}``
    - HeatMap: ``{cell.serieId}``, ``{cell.data.x}``, ``{cell.formattedValue}``
    - ScatterPlot/SwarmPlot: ``{node.serieId}``, ``{node.formattedX}``, ``{node.formattedY}``
    - Sunburst/TreeMap/CirclePacking/Icicle: ``{id}``/``{node.id}``, ``{formattedValue}``, ``{percentage}``
    - Calendar/TimeRange: ``{day}``, ``{value}``
    - Choropleth/GeoMap: ``{feature.label}``, ``{feature.formattedValue}``

    Interpolated values are HTML-escaped; the template itself may contain
    markup such as ``<strong>``. The container uses the chart theme's tooltip
    style, extended by ``style``.

    Args:
        text: The template (may be a Var).
        style: Extra inline CSS (camelCase keys) for the tooltip container.

    Returns:
        A Var holding a React component.
    """
    return FunctionStringVar.create("reflexNivoTooltip").call(text, camelize(dict(style or {})))


# --------------------------------------------------------------------------- #
# Common config objects
# --------------------------------------------------------------------------- #
def margin(
    top: int | float = 0,
    right: int | float = 0,
    bottom: int | float = 0,
    left: int | float = 0,
) -> dict[str, int | float]:
    """Chart margin.

    Returns:
        ``{"top", "right", "bottom", "left"}``.
    """
    return {"top": top, "right": right, "bottom": bottom, "left": left}


def scheme(name: str, **kwargs: Any) -> dict[str, Any]:
    """A color scheme config, e.g. ``scheme("category10")``.

    Returns:
        ``{"scheme": name, ...}``.
    """
    return {"scheme": name, **props(**kwargs)}


def inherit(source: str = "color", *modifiers: tuple[str, float]) -> dict[str, Any]:
    """An inherited color config, e.g. ``inherit("color", ("darker", 1.6))``.

    Args:
        source: The datum property to read the base color from.
        *modifiers: ``("darker" | "brighter" | "opacity", amount)`` pairs.

    Returns:
        ``{"from": source, "modifiers": [...]}``.
    """
    config: dict[str, Any] = {"from": source}
    if modifiers:
        config["modifiers"] = [list(m) for m in modifiers]
    return config


def from_theme(path: str) -> dict[str, str]:
    """A color read from the theme, e.g. ``from_theme("labels.text.fill")``.

    Returns:
        ``{"theme": path}``.
    """
    return {"theme": path}


def axis(
    *,
    legend: str | Var[str] | None = None,
    legend_position: str | None = None,
    legend_offset: int | float | None = None,
    tick_size: int | float | None = None,
    tick_padding: int | float | None = None,
    tick_rotation: int | float | None = None,
    tick_values: Any = None,
    format: Any = None,  # noqa: A002
    truncate_tick_at: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """An axis config for ``axis_top/right/bottom/left``.

    Args:
        legend: The axis legend text.
        legend_position: ``"start" | "middle" | "end"``.
        legend_offset: Legend offset in px.
        tick_size: Tick length.
        tick_padding: Space between tick and label.
        tick_rotation: Label rotation in degrees.
        tick_values: Number of ticks, explicit values, or a time interval ("every 2 days").
        format: d3-format/d3-time-format string or ``nivo.js(...)`` function.
        truncate_tick_at: Truncate long tick labels at N chars.
        **kwargs: Any other axis option (snake_case).

    Returns:
        The axis dict.
    """
    return props(
        legend=legend,
        legend_position=legend_position,
        legend_offset=legend_offset,
        tick_size=tick_size,
        tick_padding=tick_padding,
        tick_rotation=tick_rotation,
        tick_values=tick_values,
        format=format,
        truncate_tick_at=truncate_tick_at,
        **kwargs,
    )


def legend(
    *,
    anchor: LegendAnchor = "bottom-right",
    direction: LegendDirection = "column",
    translate_x: int | float = 0,
    translate_y: int | float = 0,
    item_width: int | float = 100,
    item_height: int | float = 20,
    items_spacing: int | float = 2,
    item_direction: str = "left-to-right",
    symbol_size: int | float = 12,
    symbol_shape: LegendSymbolShape = "circle",
    item_opacity: float | None = None,
    justify: bool | None = None,
    toggle_serie: bool | None = None,
    data_from: str | None = None,
    effects: Sequence[Mapping[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """A legend config for the ``legends`` prop.

    Returns:
        The legend dict.
    """
    return props(
        anchor=anchor,
        direction=direction,
        translate_x=translate_x,
        translate_y=translate_y,
        item_width=item_width,
        item_height=item_height,
        items_spacing=items_spacing,
        item_direction=item_direction,
        symbol_size=symbol_size,
        symbol_shape=symbol_shape,
        item_opacity=item_opacity,
        justify=justify,
        toggle_serie=toggle_serie,
        data_from=data_from,
        effects=list(effects) if effects is not None else None,
        **kwargs,
    )


def hover_effect(**style: Any) -> dict[str, Any]:
    """A legend hover effect, e.g. ``hover_effect(item_opacity=1)``.

    Returns:
        ``{"on": "hover", "style": {...}}``.
    """
    return {"on": "hover", "style": props(**style)}


def scale(type_: str = "linear", **kwargs: Any) -> dict[str, Any]:
    """A scale spec, e.g. ``scale("linear", min="auto", stacked=True)``.

    Time scale example: ``scale("time", format="%Y-%m-%d", precision="day")``.

    Returns:
        ``{"type": type_, ...}``.
    """
    return {"type": type_, **props(**kwargs)}


def marker(axis: str, value: Any, *, legend: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """A cartesian marker (Bar, Line, ScatterPlot).

    Returns:
        The marker dict.
    """
    return props(axis=axis, value=value, legend=legend, **kwargs)


def annotation(
    match: Mapping[str, Any],
    *,
    type_: str = "circle",
    note: str = "",
    note_x: int | float = 0,
    note_y: int | float = 0,
    offset: int | float = 4,
    note_text_offset: int | float = -3,
    **kwargs: Any,
) -> dict[str, Any]:
    """An annotation matching datums (Bar, Line, ScatterPlot, Pie, ...).

    Returns:
        The annotation dict.
    """
    return {
        "type": type_,
        "match": dict(match),
        **props(
            note=note,
            note_x=note_x,
            note_y=note_y,
            offset=offset,
            note_text_offset=note_text_offset,
            **kwargs,
        ),
    }


# --------------------------------------------------------------------------- #
# Patterns & gradients (defs / fill)
# --------------------------------------------------------------------------- #
def pattern_dots_def(
    id: str,  # noqa: A002
    *,
    color: str = "#000000",
    background: str = "#ffffff",
    size: int | float = 4,
    padding: int | float = 4,
    stagger: bool = False,
) -> dict[str, Any]:
    """A dots pattern for ``defs``."""
    return {
        "id": id,
        "type": "patternDots",
        "color": color,
        "background": background,
        "size": size,
        "padding": padding,
        "stagger": stagger,
    }


def pattern_lines_def(
    id: str,  # noqa: A002
    *,
    color: str = "#000000",
    background: str = "#ffffff",
    spacing: int | float = 5,
    rotation: int | float = 0,
    line_width: int | float = 2,
) -> dict[str, Any]:
    """A lines pattern for ``defs``."""
    return {
        "id": id,
        "type": "patternLines",
        "color": color,
        "background": background,
        "spacing": spacing,
        "rotation": rotation,
        "lineWidth": line_width,
    }


def pattern_squares_def(
    id: str,  # noqa: A002
    *,
    color: str = "#000000",
    background: str = "#ffffff",
    size: int | float = 4,
    padding: int | float = 4,
    stagger: bool = False,
) -> dict[str, Any]:
    """A squares pattern for ``defs``."""
    return {
        "id": id,
        "type": "patternSquares",
        "color": color,
        "background": background,
        "size": size,
        "padding": padding,
        "stagger": stagger,
    }


def linear_gradient_def(
    id: str,  # noqa: A002
    colors: Sequence[Mapping[str, Any]],
    **options: Any,
) -> dict[str, Any]:
    """A linear gradient for ``defs``.

    Example:
        ``linear_gradient_def("grad", [{"offset": 0, "color": "inherit"},
        {"offset": 100, "color": "inherit", "opacity": 0}])``
    """
    return {
        "id": id,
        "type": "linearGradient",
        "colors": [dict(c) for c in colors],
        **props(**options),
    }


def fill_rule(def_id: str, match: Mapping[str, Any] | str = "*") -> dict[str, Any]:
    """A ``fill`` rule applying a def to matching datums.

    Args:
        def_id: The id of a def.
        match: A dict of datum properties to match, or ``"*"`` for all.

    Returns:
        ``{"match": ..., "id": def_id}``.
    """
    return {"match": match if isinstance(match, str) else dict(match), "id": def_id}


__all__ = [
    "annotation",
    "axis",
    "camelize",
    "fill_rule",
    "from_theme",
    "hover_effect",
    "inherit",
    "js",
    "legend",
    "linear_gradient_def",
    "margin",
    "marker",
    "pattern_dots_def",
    "pattern_lines_def",
    "pattern_squares_def",
    "props",
    "scale",
    "scheme",
    "template",
    "tooltip",
]
