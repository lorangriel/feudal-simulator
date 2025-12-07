from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List


@dataclass(frozen=True)
class YearPosition:
    year: int


@dataclass(frozen=True)
class YearEntry:
    year: int
    status: str
    selectable: bool


class TimeEngine:
    """Year-based timeline manager with per-year snapshots."""

    STATUS_LOCKED = "locked"
    STATUS_PLANNING = "planning"
    STATUS_UNCREATED = "uncreated"

    def __init__(self, start_year: int = 1):
        self.history: Dict[int, Dict[str, Any]] = {}
        self.planning_state: Dict[int, Dict[str, Any]] = {}
        self.current_year: int = start_year
        self.world_state: Dict[str, Any] | None = None
        self._last_recorded_year: int | None = None

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------
    @property
    def current_position(self) -> YearPosition:
        return YearPosition(self.current_year)

    def list_years(self) -> List[int]:
        all_years: Iterable[int] = (
            list(self.history.keys())
            + list(self.planning_state.keys())
            + [self.current_year, 1]
        )
        max_year = max(all_years)
        return list(range(1, max_year + 1))

    def status(self, year: int) -> str:
        if year in self.history:
            return self.STATUS_LOCKED
        if year == self.current_year:
            return self.STATUS_PLANNING
        return self.STATUS_UNCREATED

    def is_computed(self, year: int) -> bool:
        return year in self.history

    def goto(self, year: int) -> Dict[str, Any] | None:
        if year < 1:
            year = 1
        self._ensure_planning_state(year)
        self.current_year = year
        if year in self.history:
            self.world_state = copy.deepcopy(self.history[year])
        else:
            state = self.planning_state.get(year)
            self.world_state = copy.deepcopy(state) if state is not None else None
        return self.world_state

    def prev_year(self) -> YearPosition:
        target = max(1, self.current_year - 1)
        self.goto(target)
        return self.current_position

    def next_year(self) -> YearPosition:
        self.goto(self.current_year + 1)
        return self.current_position

    def record_change(self, world_data: Dict[str, Any], reason: str | None = None):
        """Record planning changes for the current year."""

        if world_data is None:
            return
        snapshot = copy.deepcopy(world_data)
        self.planning_state[self.current_year] = snapshot
        self.world_state = snapshot
        self._last_recorded_year = self.current_year
        if reason:
            meta = snapshot.setdefault("meta", {})
            meta.setdefault("changes", []).append(reason)
        return snapshot

    def get_current_snapshot(self):
        if self.world_state is None:
            raise ValueError("No snapshot at current position")
        return copy.deepcopy(self.world_state)

    def execute_current_year(
        self, executor: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None
    ) -> YearPosition:
        if self.world_state is None:
            return self.current_position
        working_state = copy.deepcopy(self.world_state)
        if executor:
            working_state = executor(working_state)
        snapshot = copy.deepcopy(working_state)
        self.history[self.current_year] = snapshot
        self.planning_state[self.current_year] = copy.deepcopy(snapshot)
        self.current_year += 1
        self._ensure_planning_state(self.current_year, base_state=snapshot)
        self.world_state = copy.deepcopy(self.planning_state[self.current_year])
        return self.current_position

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def get_year_entries(self) -> List[YearEntry]:
        entries: List[YearEntry] = []
        for year in self.list_years():
            status = self.status(year)
            selectable = year == 1 or status != self.STATUS_UNCREATED
            entries.append(YearEntry(year, status, selectable))
        return entries

    def reset_timeline(
        self, world_state: Dict[str, Any] | None = None, start_year: int = 1, **_
    ) -> None:
        self.history = {}
        self.planning_state = {}
        self.current_year = max(1, start_year)
        self.world_state = copy.deepcopy(world_state) if world_state is not None else None
        if self.world_state is not None:
            self.planning_state[self.current_year] = copy.deepcopy(self.world_state)
        self._last_recorded_year = None

    def _ensure_planning_state(
        self, year: int, base_state: Dict[str, Any] | None = None
    ) -> None:
        if year in self.planning_state:
            return
        template = (
            copy.deepcopy(base_state)
            if base_state is not None
            else copy.deepcopy(self.world_state)
        )
        self.planning_state[year] = template or {}

