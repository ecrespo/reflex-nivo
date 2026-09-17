"""Constants shared by every nivo component."""

from __future__ import annotations

from typing import Literal

# Every @nivo/* package is released in lockstep, so a single version pin keeps
# all charts (and their shared @nivo/core, @nivo/theming, ...) consistent.
NIVO_VERSION = "0.99.0"


def nivo_package(name: str) -> str:
    """Return the pinned npm specifier for a nivo package.

    Args:
        name: The package name without scope, e.g. ``"bar"``.

    Returns:
        The npm specifier, e.g. ``"@nivo/bar@0.99.0"``.
    """
    return f"@nivo/{name}@{NIVO_VERSION}"


# Categorical, diverging and sequential schemes from @nivo/colors.
# Use them as ``colors={"scheme": "nivo"}``.
CATEGORICAL_COLOR_SCHEMES = (
    "nivo",
    "category10",
    "accent",
    "dark2",
    "paired",
    "pastel1",
    "pastel2",
    "set1",
    "set2",
    "set3",
    "tableau10",
)
DIVERGING_COLOR_SCHEMES = (
    "brown_blueGreen",
    "purpleRed_green",
    "pink_yellowGreen",
    "purple_orange",
    "red_blue",
    "red_grey",
    "red_yellow_blue",
    "red_yellow_green",
    "spectral",
)
SEQUENTIAL_COLOR_SCHEMES = (
    "blues",
    "greens",
    "greys",
    "oranges",
    "purples",
    "reds",
    "blue_green",
    "blue_purple",
    "green_blue",
    "orange_red",
    "purple_blue_green",
    "purple_blue",
    "purple_red",
    "red_purple",
    "yellow_green_blue",
    "yellow_green",
    "yellow_orange_brown",
    "yellow_orange_red",
)
COLOR_SCHEMES = CATEGORICAL_COLOR_SCHEMES + DIVERGING_COLOR_SCHEMES + SEQUENTIAL_COLOR_SCHEMES

# d3-shape curve identifiers accepted by Line, Stream, Bump, ParallelCoordinates...
CURVES = (
    "basis",
    "cardinal",
    "catmullRom",
    "linear",
    "monotoneX",
    "monotoneY",
    "natural",
    "step",
    "stepAfter",
    "stepBefore",
)

# react-spring presets accepted by ``motion_config``.
MOTION_CONFIGS = ("default", "gentle", "wobbly", "stiff", "slow", "molasses")

# Anchors accepted by legends and annotations.
LegendAnchor = Literal[
    "top",
    "top-right",
    "right",
    "bottom-right",
    "bottom",
    "bottom-left",
    "left",
    "top-left",
    "center",
]
LegendDirection = Literal["row", "column"]
LegendSymbolShape = Literal["circle", "diamond", "square", "triangle"]
ScaleType = Literal["linear", "log", "symlog", "point", "band", "time"]
