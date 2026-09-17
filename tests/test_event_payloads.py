"""What each nivo callback hands the Python handler.

Every nivo callback but one passes an object (datum, node, cell, point...).
`onActiveIdChange` passes `DatumId | null`, a bare string/number, so declaring
it as a dict makes every handler annotation and stub wrong.
"""

from __future__ import annotations

from typing import Any

import pytest
import reflex_nivo as nivo
from reflex.vars.base import Var


def _payload_type(chart: type, event: str) -> Any:
    """The type the chart declares for an event's single argument."""
    spec = chart.get_event_triggers()[event]
    return spec(Var(_js_expr="_arg"))[0]._var_type


@pytest.mark.parametrize("chart", [nivo.Pie, nivo.PieCanvas], ids=lambda c: c.__name__)
def test_active_id_change_declares_a_scalar_id(chart):
    assert _payload_type(chart, "on_active_id_change") != dict[str, Any]


@pytest.mark.parametrize(
    ("chart", "event"),
    [(nivo.Pie, "on_click"), (nivo.Bar, "on_click"), (nivo.Sankey, "on_click")],
    ids=lambda value: getattr(value, "__name__", str(value)),
)
def test_the_other_callbacks_still_declare_a_datum(chart, event):
    assert _payload_type(chart, event) == dict[str, Any]
