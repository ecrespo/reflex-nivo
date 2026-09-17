"""reflex-nivo: every nivo (https://nivo.rocks) chart as a Reflex component.

Usage::

    import reflex_nivo as nivo

    nivo.bar(data=State.rows, keys=["a", "b"], index_by="country", height="420px")
"""

from . import themes
from .base import NivoComponent, nivo_event_spec
from .charts import *  # noqa: F403
from .charts import __all__ as _charts_all
from .constants import (
    CATEGORICAL_COLOR_SCHEMES,
    COLOR_SCHEMES,
    CURVES,
    DIVERGING_COLOR_SCHEMES,
    MOTION_CONFIGS,
    NIVO_VERSION,
    SEQUENTIAL_COLOR_SCHEMES,
)
from .helpers import *  # noqa: F403
from .helpers import __all__ as _helpers_all

__version__ = "0.1.0"

__all__ = [
    "CATEGORICAL_COLOR_SCHEMES",
    "COLOR_SCHEMES",
    "CURVES",
    "DIVERGING_COLOR_SCHEMES",
    "MOTION_CONFIGS",
    "NIVO_VERSION",
    "SEQUENTIAL_COLOR_SCHEMES",
    "NivoComponent",
    "nivo_event_spec",
    "themes",
    *_charts_all,
    *_helpers_all,
]
