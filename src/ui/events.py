"""Central eventkoppling mellan paneler."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


class UIEventBus:
    """Enkel signal-hub för panelinteraktioner."""

    def __init__(self):
        self._selection_listeners: list[Callable[[str | None], None]] = []
        self._listeners: dict[str, list[Callable[..., None]]] = {}

    def on(self, event_name: str, callback: Callable[..., None]) -> None:
        self._listeners.setdefault(event_name, []).append(callback)

    def emit(self, event_name: str, **payload: Any) -> None:
        for callback in list(self._listeners.get(event_name, [])):
            callback(**payload)

    def on_selection_changed(self, callback: Callable[[str | None], None]) -> None:
        self._selection_listeners.append(callback)

    def emit_selection(self, resource_name: str | None) -> None:
        for callback in list(self._selection_listeners):
            callback(resource_name)
