import copy
from dataclasses import dataclass
from typing import Any, Dict, Tuple

SEASON_COUNT = 4
SEASON_LABELS = {0: "vår", 1: "sommar", 2: "höst", 3: "vinter"}


@dataclass(frozen=True)
class TimePosition:
    year: int
    season_index: int

    @property
    def season(self) -> int:
        return self.season_index


class TimeEngine:
    def __init__(self):
        # (year, season) → deepcopied world snapshot
        self.history: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self.current: Tuple[int, int] = (0, 0)  # adjust if needed
        self.max_past: Tuple[int, int] = (0, 0)
        self.max_future: Tuple[int, int] = (0, 0)
        self.world_state: Dict[str, Any] | None = None
        self.future_invalidated = False

    @property
    def current_position(self) -> TimePosition:
        year, season = self.current
        return TimePosition(year, season)

    def record_change(self, world_data, reason=None):
        """
        Deepcopy snapshot into history at current time.
        Trim any future timeline beyond current.
        """

        snapshot = copy.deepcopy(world_data)
        self.history[self.current] = snapshot
        self.world_state = snapshot

        removed_future = False
        for key in list(self.history.keys()):
            if self._is_future(key, self.current):
                del self.history[key]
                removed_future = True

        self._update_bounds()
        if removed_future:
            self.future_invalidated = True
        elif self._timeline_is_continuous():
            self.future_invalidated = False
        return snapshot

    def goto(self, year: int, season: int):
        """
        Move current pointer. If snapshot missing → error.
        Return deepcopy of snapshot.
        """

        key = (year, season)
        if key not in self.history:
            raise ValueError(f"Missing snapshot for {key}")
        self.current = key
        snapshot = copy.deepcopy(self.history[key])
        self.world_state = snapshot
        return snapshot

    def step(self, direction: int):
        """
        +1 or -1 season. Wrap year correctly.
        Return deepcopy of new snapshot.
        """

        year, season = self.current
        season += direction
        while season < 0:
            year -= 1
            season += SEASON_COUNT
        if season >= SEASON_COUNT:
            year += season // SEASON_COUNT
            season = season % SEASON_COUNT
        next_key = (year, season)
        if next_key not in self.history:
            current_snapshot = self.history.get(self.current)
            if current_snapshot is None:
                raise ValueError("No snapshots recorded to step from")
            self.history[next_key] = copy.deepcopy(current_snapshot)
            self._update_bounds()
        return self.goto(year, season)

    def get_current_snapshot(self):
        """Return deepcopy of world at current pointer."""

        if self.current not in self.history:
            raise ValueError("No snapshot at current position")
        return copy.deepcopy(self.history[self.current])

    def can_jump_decade(self):
        """
        Return True if timeline is continuous (no gaps)
        and no invalidated future exists.
        """

        return self._timeline_is_continuous() and not self.future_invalidated

    # Compatibility helpers -------------------------------------------------
    def allows_decade_jumps(self):
        return self.can_jump_decade()

    def step_seasons(self, delta: int):
        step_dir = 1 if delta >= 0 else -1
        for _ in range(abs(delta)):
            self.step(step_dir)
        year, season = self.current
        return TimePosition(year, season)

    def reset_timeline(self, world_state: Dict[str, Any] | None = None, **_):
        self.history = {}
        self.current = (0, 0)
        self.future_invalidated = False
        if world_state is not None:
            self.record_change(world_state)

    # Internal helpers ------------------------------------------------------
    def _update_bounds(self):
        if not self.history:
            self.max_past = (0, 0)
            self.max_future = (0, 0)
            return
        keys = sorted(self.history.keys())
        self.max_past = keys[0]
        self.max_future = keys[-1]

    def _is_future(self, key: Tuple[int, int], current: Tuple[int, int]):
        return key[0] > current[0] or (key[0] == current[0] and key[1] > current[1])

    def _timeline_is_continuous(self):
        if not self.history:
            return False
        keys = sorted(self.history.keys())
        start_index = keys[0][0] * SEASON_COUNT + keys[0][1]
        end_index = keys[-1][0] * SEASON_COUNT + keys[-1][1]
        expected = end_index - start_index + 1
        return expected == len(keys)
