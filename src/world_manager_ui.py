from __future__ import annotations

from typing import Any, Callable, Dict

from data_manager import save_worlds_to_file


class WorldManagerUI:
    """High level world data operations used by the UI."""

    def __init__(
        self, save_func: Callable[[Dict[str, Any]], None] = save_worlds_to_file
    ) -> None:
        self._save_func = save_func

    def save_current_world(
        self,
        active_world: str | None,
        world_data: Dict[str, Any] | None,
        all_worlds: Dict[str, Any],
        refresh_cb: Callable[[], None] | None = None,
    ) -> None:
        """Persist ``world_data`` and refresh any viewers."""
        if active_world and world_data is not None:
            all_worlds[active_world] = world_data
            self.persist_worlds(all_worlds)
            if refresh_cb:
                refresh_cb()

    def persist_worlds(self, all_worlds: Dict[str, Any]) -> None:
        """Write ``all_worlds`` to storage."""
        self._save_func(all_worlds)
