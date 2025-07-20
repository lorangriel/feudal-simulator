from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class WorldInterface(ABC):
    """Interface defining operations on world data."""

    def __init__(self, world_data: Dict[str, Any] | None = None) -> None:
        self.world_data = world_data or {}

    def set_world_data(self, world_data: Dict[str, Any]) -> None:
        """Update the reference to the active world data."""
        self.world_data = world_data

    @abstractmethod
    def get_depth_of_node(self, node_id: int) -> int:
        pass

    @abstractmethod
    def get_display_name_for_node(self, node_data: Dict[str, Any] | Any, depth: int) -> str:
        pass

    @abstractmethod
    def update_subfiefs_for_node(self, node_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def delete_node_and_descendants(self, node_id: int) -> int:
        pass

    @abstractmethod
    def attempt_link_neighbors(self, node_id1: int, node_id2: int) -> tuple[bool, str]:
        """Link two jarldoms. Returns success flag and status message."""
        pass
