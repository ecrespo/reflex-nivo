"""Shared demo state: the event inspector fed by every chart callback."""

from __future__ import annotations

import json
from typing import Any

import reflex as rx


class EventLog(rx.State):
    """Last events received from nivo charts."""

    source: str = ""
    event: str = ""
    payload: str = ""
    history: list[dict[str, str]] = []

    @rx.event
    def record(self, source: str, event: str, payload: Any):
        """Store an event coming from a chart.

        Args:
            source: The chart that fired it.
            event: The nivo callback name.
            payload: The sanitized datum sent by reflex-nivo.
        """
        text = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
        if len(text) > 1800:
            text = text[:1800] + "\n… (truncated)"
        self.source, self.event, self.payload = source, event, text
        self.history = [{"source": source, "event": event}, *self.history][:6]

    @rx.event
    def clear(self):
        """Reset the inspector."""
        self.source, self.event, self.payload, self.history = "", "", "", []


def log(source: str, event: str = "on_click"):
    """Build an event handler lambda that records a chart event.

    Args:
        source: Label shown in the inspector.
        event: Callback name shown in the inspector.

    Returns:
        A lambda usable as a nivo event trigger.
    """
    return lambda datum: EventLog.record(source, event, datum)
