"""Calendar dates must not shift a day (and a year) west of Greenwich.

nivo does `new Date("2025-01-01")`, which JS parses as UTC midnight, so a plain
date has to be sent as local midnight. That has to happen whether the date is
written in the page or comes from state, which is the normal Reflex pattern.
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest
import reflex as rx
import reflex_nivo as nivo
from reflex_nivo.base import NivoComponent


class _State(rx.State):
    start: str = "2025-01-01"
    end: str = "2025-12-31"


def test_a_literal_date_is_sent_as_local_midnight():
    rendered = str(nivo.calendar(data=[], from_date="2025-01-01", to_date="2025-12-31"))
    assert 'from:"2025-01-01T00:00:00"' in rendered
    assert 'to:"2025-12-31T00:00:00"' in rendered


@pytest.mark.parametrize("prop", ["from_date", "to_date"])
def test_a_date_from_state_is_normalized_too(prop):
    """A Var used to travel untouched, so nivo read it as UTC midnight."""
    rendered = str(nivo.calendar(data=[], **{prop: _State.start}))
    bare = str(_State.start)
    nivo_name = {"from_date": "from", "to_date": "to"}[prop]
    assert f"{nivo_name}:{bare}" not in rendered, "the state var reaches nivo unnormalized"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_date_helper_only_touches_plain_dates():
    script = (
        "".join(NivoComponent.add_custom_code(nivo.calendar(data=[]).children[0]))
        + """
        console.log(JSON.stringify({
            plain: reflexNivoDate("2025-01-01"),
            withTime: reflexNivoDate("2025-01-01T09:30:00"),
            other: reflexNivoDate("not a date"),
            number: reflexNivoDate(1735689600000),
        }));
        """
    )
    out = json.loads(
        subprocess.run(
            [shutil.which("node"), "--input-type=module", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    assert out == {
        "plain": "2025-01-01T00:00:00",
        "withTime": "2025-01-01T09:30:00",
        "other": "not a date",
        "number": 1735689600000,
    }
