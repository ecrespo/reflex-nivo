"""Ready-made nivo themes that follow Reflex's light/dark color mode.

nivo draws everything with inline styles (SVG) or directly on a ``<canvas>``,
so it cannot pick up CSS variables reliably. These themes therefore use
concrete colors taken from the Radix Themes gray scale and switch between the
light and dark variant with :func:`reflex.color_mode_cond`.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import reflex as rx
from reflex.vars.base import Var

_FONT = "var(--default-font-family, Inter, system-ui, sans-serif)"


def _build(
    *,
    text: str,
    text_muted: str,
    grid: str,
    domain: str,
    panel: str,
    border: str,
    label_outline: str,
) -> dict[str, Any]:
    return {
        "background": "transparent",
        "text": {"fontSize": 11, "fill": text, "fontFamily": _FONT},
        "axis": {
            "domain": {"line": {"stroke": domain, "strokeWidth": 1}},
            "legend": {"text": {"fontSize": 12, "fill": text, "fontWeight": 600}},
            "ticks": {
                "line": {"stroke": domain, "strokeWidth": 1},
                "text": {"fontSize": 11, "fill": text_muted},
            },
        },
        "grid": {"line": {"stroke": grid, "strokeWidth": 1}},
        "legends": {
            "title": {"text": {"fontSize": 11, "fill": text}},
            "text": {"fontSize": 11, "fill": text},
            "ticks": {
                "line": {},
                "text": {"fontSize": 10, "fill": text_muted},
            },
        },
        "annotations": {
            "text": {
                "fontSize": 13,
                "fill": text,
                "outlineWidth": 2,
                "outlineColor": label_outline,
                "outlineOpacity": 1,
            },
            "link": {
                "stroke": text,
                "strokeWidth": 1,
                "outlineWidth": 2,
                "outlineColor": label_outline,
                "outlineOpacity": 1,
            },
            "outline": {
                "stroke": text,
                "strokeWidth": 2,
                "outlineWidth": 2,
                "outlineColor": label_outline,
                "outlineOpacity": 1,
            },
            "symbol": {
                "fill": text,
                "outlineWidth": 2,
                "outlineColor": label_outline,
                "outlineOpacity": 1,
            },
        },
        "labels": {"text": {"fill": text}},
        "dots": {"text": {"fill": text}},
        "markers": {"lineColor": text_muted, "textColor": text},
        "crosshair": {"line": {"stroke": text, "strokeWidth": 1, "strokeOpacity": 0.5}},
        "tooltip": {
            "wrapper": {},
            "container": {
                "background": panel,
                "color": text,
                "fontSize": 12,
                "fontFamily": _FONT,
                "borderRadius": 6,
                "border": f"1px solid {border}",
                "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.18)",
                "padding": "6px 10px",
            },
            "basic": {},
            "chip": {},
            "table": {},
            "tableCell": {"padding": "3px 5px"},
            "tableCellValue": {"fontWeight": 600},
        },
    }


LIGHT: dict[str, Any] = _build(
    text="#1c2024",
    text_muted="#60646c",
    grid="#e8e8ec",
    domain="#b9bbc6",
    panel="#ffffff",
    border="#e0e1e6",
    label_outline="#ffffff",
)
"""A light nivo theme (Radix gray scale)."""

DARK: dict[str, Any] = _build(
    text="#edeef0",
    text_muted="#b0b4ba",
    grid="#2e3135",
    domain="#5a6169",
    panel="#212225",
    border="#363a3f",
    label_outline="#111113",
)
"""A dark nivo theme (Radix gray scale)."""


def merge(base: dict[str, Any], overrides: dict[str, Any] | None) -> dict[str, Any]:
    """Deep-merge ``overrides`` into a copy of ``base``.

    Args:
        base: The theme to start from.
        overrides: Partial theme whose keys win over ``base``.

    Returns:
        A new theme dictionary.
    """
    result = copy.deepcopy(base)
    for key, value in (overrides or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


_LIGHT_CONST = "reflexNivoLightTheme"
_DARK_CONST = "reflexNivoDarkTheme"


def auto(
    overrides: dict[str, Any] | None = None,
    *,
    light: dict[str, Any] | None = None,
    dark: dict[str, Any] | None = None,
) -> Var:
    """Build a theme Var that follows the app's color mode.

    Args:
        overrides: Partial theme merged into both the light and dark variants.
        light: Extra overrides applied only in light mode.
        dark: Extra overrides applied only in dark mode.

    Returns:
        A Var evaluating to the light or dark theme depending on color mode.
    """
    if overrides is None and light is None and dark is None:
        # The common case: point at the literals injected once per page rather
        # than serializing both themes into every chart's props.
        return rx.color_mode_cond(
            light=Var(_js_expr=_LIGHT_CONST, _var_type=dict),
            dark=Var(_js_expr=_DARK_CONST, _var_type=dict),
        )
    light_theme = merge(merge(LIGHT, overrides), light)
    dark_theme = merge(merge(DARK, overrides), dark)
    return rx.color_mode_cond(light=light_theme, dark=dark_theme)


def js_constants() -> str:
    """The shared theme literals, injected once per page.

    Returns:
        A JavaScript snippet declaring the light and dark theme constants.
    """
    return f"const {_LIGHT_CONST} = {json.dumps(LIGHT)};\nconst {_DARK_CONST} = {json.dumps(DARK)};"


__all__ = ["DARK", "LIGHT", "auto", "js_constants", "merge"]
