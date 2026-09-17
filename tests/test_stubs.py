"""The stubs must describe what `create()` really returns.

Every factory returns the wrapping `<div>`, never the chart class, so a stub
that promises the chart lets a type checker accept nivo-only attribute access
and reject valid container usage.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import reflex as rx
import reflex_nivo as nivo
from reflex_nivo.charts import __all__ as CHART_NAMES

PACKAGE = Path(nivo.__file__).parent
STUBS = [*sorted(PACKAGE.glob("charts/*.pyi")), PACKAGE / "base.pyi"]
CLASSES = [name for name in CHART_NAMES if name[0].isupper()]


@pytest.mark.parametrize("name", CLASSES)
def test_create_returns_the_container_at_runtime(name):
    chart = getattr(nivo, name)
    kwargs = {"data": []} if "data" in chart.get_props() else {"features": []}
    assert isinstance(chart.create(**kwargs), rx.Component)
    assert not isinstance(chart.create(**kwargs), chart)


@pytest.mark.parametrize("stub", STUBS, ids=lambda p: p.name)
def test_stubs_do_not_promise_the_chart_class(stub):
    returns = re.findall(r"\)\s*->\s*(.+?):\s*$", stub.read_text(), re.MULTILINE)
    assert returns, f"{stub.name} declares no create()"
    assert all(value == "Component" for value in returns), returns
