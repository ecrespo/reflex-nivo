"""Base class and runtime helpers shared by all nivo components."""

from __future__ import annotations

import difflib
import functools
import re
from typing import Any, ClassVar, Literal

import reflex as rx
from reflex.components.component import Component
from reflex.utils.imports import ImportDict, ImportVar
from reflex.vars.base import Var

from . import themes
from ._css import CSS_PROPERTIES
from .constants import nivo_package

# --------------------------------------------------------------------------- #
# JavaScript helpers injected once per page.
# --------------------------------------------------------------------------- #

# nivo hands event callbacks rich objects: d3 hierarchy nodes with `parent`
# back-references, sankey nodes whose links point back to them, React
# synthetic events, DOM elements, Dates... None of that survives JSON
# serialization, so every event payload goes through this sanitizer before
# being sent to the Reflex backend. Repeated/cyclic objects are replaced by
# their `id` (or dropped), functions and DOM nodes are removed, Dates become
# ISO strings and the recursion depth is bounded. The bound is deep enough for
# the hierarchy datums (tree, sunburst, icicle...) that drill-down handlers
# send straight back to a chart.
_SERIALIZE_JS = r"""
const reflexNivoSerialize = (value, depth = 0, seen = new WeakSet()) => {
  if (value === null || value === undefined) return null;
  const kind = typeof value;
  if (kind === "number") return Number.isFinite(value) ? value : null;
  if (kind === "string" || kind === "boolean") return value;
  if (kind === "bigint") return value.toString();
  if (kind === "function" || kind === "symbol") return undefined;
  if (value instanceof Date) return value.toISOString();
  if (typeof Node !== "undefined" && value instanceof Node) return undefined;
  if (typeof Event !== "undefined" && value instanceof Event) return undefined;
  if (value.nativeEvent !== undefined && value.currentTarget !== undefined) return undefined;
  if (seen.has(value)) return value.id !== undefined ? reflexNivoSerialize(value.id, depth, seen) : undefined;
  if (depth > 12) return undefined;
  seen.add(value);
  if (Array.isArray(value)) {
    // Dropped entries (too deep, cyclic, a DOM node...) are skipped rather
    // than turned into nulls: a hierarchy datum sent back to a chart as
    // `data=` must not contain a null child, which d3-hierarchy cannot read.
    const items = [];
    for (const item of value.slice(0, 2000)) {
      const serialized = reflexNivoSerialize(item, depth + 1, seen);
      if (serialized !== undefined) items.push(serialized);
    }
    return items;
  }
  const result = {};
  for (const key of Object.keys(value)) {
    const serialized = reflexNivoSerialize(value[key], depth + 1, seen);
    if (serialized !== undefined) result[key] = serialized;
  }
  return result;
};
"""

# String templates: "{id}: {formattedValue}" -> function reading dotted paths
# from the object nivo passes (datum, point, node, cell...).
_TEMPLATE_JS = r"""
const reflexNivoGet = (obj, path) => path.split(".").reduce((acc, key) => (acc === null || acc === undefined ? undefined : acc[key]), obj);
const reflexNivoEscape = (text) => String(text).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const reflexNivoFormat = (template, source, escape) => String(template).replace(/\{\s*([\w$.]+)\s*\}/g, (_, path) => {
  const raw = reflexNivoGet(source, path);
  const text = raw === null || raw === undefined ? "" : (typeof raw === "object" ? JSON.stringify(reflexNivoSerialize(raw)) : String(raw));
  return escape ? reflexNivoEscape(text) : text;
});
const reflexNivoTemplateCache = new Map();
const reflexNivoTemplate = (template) => {
  const cacheKey = "template:" + template;
  if (!reflexNivoTemplateCache.has(cacheKey)) {
    reflexNivoTemplateCache.set(cacheKey, (source) => reflexNivoFormat(template, source, false));
  }
  return reflexNivoTemplateCache.get(cacheKey);
};
const reflexNivoTooltip = (template, style) => {
  const cacheKey = "tooltip:" + template + "::" + JSON.stringify(style || {});
  if (!reflexNivoTemplateCache.has(cacheKey)) {
    const NivoTemplateTooltip = (props) => {
      const theme = reflexNivoUseTheme();
      const container = (theme && theme.tooltip && theme.tooltip.container) || {};
      return reflexNivoCreateElement("div", {
        style: { ...container, whiteSpace: "pre", ...(style || {}) },
        dangerouslySetInnerHTML: { __html: reflexNivoFormat(template, props, true) },
      });
    };
    reflexNivoTemplateCache.set(cacheKey, NivoTemplateTooltip);
  }
  return reflexNivoTemplateCache.get(cacheKey);
};
"""


def nivo_event_spec(datum: Var[Any]) -> tuple[Var[dict[str, Any]]]:
    """Event spec shared by every nivo callback.

    nivo always passes the interesting payload (datum, point, node, cell,
    serie, feature, dimensions, active id...) as the first argument. It is
    sanitized in the browser so it can be serialized to the backend.

    Args:
        datum: The first argument of the nivo callback.

    Returns:
        A one-element tuple with the JSON-safe payload.
    """
    return (Var(_js_expr=f"reflexNivoSerialize({datum!s})", _var_type=dict[str, Any]),)


_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")

# An explicit None prop: nivo must receive null, not nothing at all.
_JS_NULL = Var(_js_expr="null", _var_type=None)

# Non-CSS props forwarded to the wrapping <div>.
_CONTAINER_PROPS = frozenset({"id", "class_name", "style", "title", "tab_index"})


def _style_shorthands() -> frozenset[str]:
    """Reflex's own style shorthands (``margin_x``, ``bg``...).

    They are not CSS property names, so ``CSS_PROPERTIES`` does not list them,
    but they are valid on any Reflex component and must reach the container.

    Returns:
        The snake_case shorthand names supported by the installed Reflex.
    """
    try:
        from reflex_base.style import STYLE_PROP_SHORTHAND_MAPPING
    except ImportError:  # pragma: no cover - older/newer Reflex layout
        return frozenset({"bg", "bg_color", "margin_x", "margin_y", "padding_x", "padding_y"})
    return frozenset(re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower() for name in STYLE_PROP_SHORTHAND_MAPPING)


_STYLE_SHORTHANDS = _style_shorthands()


@functools.lru_cache(maxsize=1)
def _container_event_names() -> frozenset[str]:
    """The DOM events the wrapping ``<div>`` accepts.

    Returns:
        The container's ``on_*`` trigger names.
    """
    return frozenset(type(rx.el.div()).get_event_triggers())


class NivoComponent(Component):
    """Base for every nivo chart.

    Subclasses wrap the ``Responsive*`` export of a nivo package. Calling
    ``create`` returns the chart wrapped in a sized ``<div>``: nivo's
    responsive charts fill their parent, so the parent must have a height.
    Any keyword argument that is not a nivo prop or event (``width``,
    ``height``, ``min_height``, ``class_name``, ``style``, ``id``...) is
    applied to that container.
    """

    library = nivo_package("core")

    # "svg", "canvas" or "html" -- informational, used by the demo/docs.
    _nivo_variant: ClassVar[Literal["svg", "canvas", "html"]] = "svg"

    # nivo props applied when the caller does not pass them.
    _default_props: ClassVar[dict[str, Any]] = {}

    # Default container size.
    _default_width: ClassVar[str] = "100%"
    _default_height: ClassVar[str] = "400px"

    # Python-safe names for nivo props that clash with Python keywords or
    # with Reflex's own component fields (``id``).
    _rename_props: ClassVar[dict[str, str]] = {
        "idBy": "id",
        "fromDate": "from",
        "toDate": "to",
    }

    def add_imports(self) -> ImportDict:
        """Imports needed by the injected JS helpers.

        Returns:
            The import dictionary.
        """
        return {
            "react": [ImportVar(tag="createElement", alias="reflexNivoCreateElement")],
            nivo_package("theming"): [ImportVar(tag="useTheme", alias="reflexNivoUseTheme")],
        }

    def add_custom_code(self) -> list[str]:
        """JS helpers for event payloads, templates and tooltips.

        Returns:
            The custom code blocks (deduplicated per page by Reflex).
        """
        return [_SERIALIZE_JS.strip(), _TEMPLATE_JS.strip()]

    @classmethod
    def _nivo_event_names(cls) -> set[str]:
        """The nivo callbacks this chart declares.

        ``get_event_triggers()`` also reports the triggers every Reflex
        component inherits (``on_click``, ``on_mouse_move``...). nivo never
        reads those, so a chart that does not declare them must let them
        through to the wrapping ``<div>`` instead of swallowing them.

        Returns:
            The ``on_*`` names declared by the chart classes themselves.
        """
        names: set[str] = set()
        for klass in cls.__mro__:
            if klass is NivoComponent:
                break
            for name, annotation in vars(klass).get("__annotations__", {}).items():
                if name.startswith("on_") and "EventHandler" in str(annotation):
                    names.add(name)
        return names

    @classmethod
    def _chart_prop_names(cls) -> set[str]:
        names = set(cls.get_props()) | cls._nivo_event_names()
        return names | {"key", "custom_attrs", "special_props"}

    @classmethod
    def _is_container_prop(cls, name: str) -> bool:
        if name in _CONTAINER_PROPS or name in CSS_PROPERTIES or name in _STYLE_SHORTHANDS:
            return True
        if name.startswith("on_"):
            # A DOM event on the container: it fires for the whole chart area.
            return name in _container_event_names()
        # Reflex pseudo selectors (_hover, _dark...) and responsive/aria/data attrs.
        return name.startswith(("_", "aria_", "data_"))

    @classmethod
    def create(cls, *children: Any, **props: Any) -> Component:  # type: ignore[override]
        """Create the chart wrapped in a sized container.

        Args:
            *children: Ignored by nivo; accepted for API symmetry.
            **props: nivo props/events (snake_case) plus container props.

        Returns:
            A ``<div>`` containing the nivo chart.
        """
        chart_names = cls._chart_prop_names()
        chart_props: dict[str, Any] = {}
        container_props: dict[str, Any] = {}
        for name, value in props.items():
            if name in chart_names:
                chart_props[name] = value
            elif cls._is_container_prop(name):
                container_props[name] = value
            else:
                candidates = sorted(cls._nivo_event_names() if name.startswith("on_") else chart_names)
                suggestion = difflib.get_close_matches(name, candidates, n=1)
                hint = f" Did you mean {suggestion[0]!r}?" if suggestion else ""
                if name.startswith("on_"):
                    msg = (
                        f"{cls.__name__} got an unexpected event {name!r}: {cls.tag} has no such "
                        f"nivo callback and the container does not fire it either. "
                        f"nivo callbacks on this chart: {', '.join(candidates) or 'none'}.{hint}"
                    )
                else:
                    msg = (
                        f"{cls.__name__} got an unexpected prop {name!r}: it is neither a "
                        f"nivo prop of {cls.tag} nor a CSS property for the container.{hint}"
                    )
                raise TypeError(msg)

        # nivo does `new Date("2025-01-01")`, which JS parses as UTC midnight:
        # west of Greenwich that is the previous day (and year). Plain dates
        # are therefore sent as local midnight.
        for name in ("from_date", "to_date"):
            value = chart_props.get(name)
            if isinstance(value, str) and _ISO_DATE.fullmatch(value):
                chart_props[name] = f"{value}T00:00:00"

        for name, value in cls._default_props.items():
            chart_props.setdefault(name, value)

        # Follow Reflex's light/dark mode unless the caller provided a theme.
        # An explicit `theme=None` means nivo's own theme, like any other prop.
        if "theme" in chart_names and "theme" not in chart_props:
            chart_props["theme"] = themes.auto()

        # Reflex drops props whose value is None, which would leave nivo
        # applying its own default (`axisBottom = {}`) instead of hiding the
        # axis. An explicit None is what the docs call "None to hide", so it
        # travels as JavaScript null: React defaults only fill in `undefined`.
        for name, value in chart_props.items():
            if value is None:
                chart_props[name] = _JS_NULL

        container_props.setdefault("width", cls._default_width)
        container_props.setdefault("height", cls._default_height)
        container_props.setdefault("position", "relative")

        chart = super().create(*children, **chart_props)
        return rx.el.div(chart, **container_props)


__all__ = ["NivoComponent", "nivo_event_spec"]
