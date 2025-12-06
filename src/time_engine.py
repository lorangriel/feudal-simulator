"""Tidsmotor för år/årstider, snapshots och deterministisk PRNG.

Modulen kapslar tidslinjehantering, snapshotting och event-loggning. Den är
frikopplad från UI:t men används av FeodalSimulator för att driva de nya
tidsknapparna.
"""

from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from weather import roll_weather


SEASONS = ["spring", "summer", "autumn", "winter"]
SEASON_LABELS = {
    "spring": "vår",
    "summer": "sommar",
    "autumn": "höst",
    "winter": "vinter",
}
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class TimePosition:
    """Represents a specific year/season."""

    year: int
    season_index: int

    @classmethod
    def from_season(cls, year: int, season: str) -> "TimePosition":
        if season not in SEASONS:
            raise ValueError(f"Unknown season '{season}'")
        return cls(year, SEASONS.index(season))

    @property
    def season(self) -> str:
        return SEASONS[self.season_index % len(SEASONS)]

    def step(self, delta: int) -> "TimePosition":
        season_count = self.year * len(SEASONS) + self.season_index + delta
        new_year, new_season_index = divmod(season_count, len(SEASONS))
        return TimePosition(new_year, new_season_index)

    def __lt__(self, other: "TimePosition") -> bool:  # type: ignore[override]
        return (self.year, self.season_index) < (other.year, other.season_index)

    def __le__(self, other: "TimePosition") -> bool:  # type: ignore[override]
        return (self.year, self.season_index) <= (other.year, other.season_index)

    def __hash__(self) -> int:  # pragma: no cover - dataclass fallback is fine
        return hash((self.year, self.season_index))


def _serialize_seed_parts(parts: Iterable[Any]) -> int:
    joined = "::".join(str(p) for p in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def rng_for(
    timeline_id: str,
    year: int,
    season: str,
    node_id: Optional[int] = None,
    subsystem_tag: Optional[str] = None,
    base_seed: int | None = None,
) -> random.Random:
    """Return a deterministic ``Random`` instance for the given tuple.

    The seed is derived from ``timeline_id``, ``year``, ``season``, optional
    ``node_id`` and ``subsystem_tag`` plus an optional ``base_seed`` to anchor a
    timeline-wide randomness stream.
    """

    parts: List[Any] = [timeline_id, year, season, node_id or "*"]
    if subsystem_tag:
        parts.append(subsystem_tag)
    if base_seed is not None:
        parts.append(base_seed)
    seed = _serialize_seed_parts(parts)
    return random.Random(seed)


class SnapshotStore:
    """Persist snapshots and events to a JSON file."""

    def __init__(self, base_path: Path, timeline_id: str) -> None:
        self.base_path = base_path
        self.timeline_id = timeline_id
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.path = self.base_path / f"timeline_{timeline_id}.json"

    def load(self) -> dict | None:
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def save(self, data: dict) -> None:
        tmp_path = self.path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        tmp_path.replace(self.path)


class TimeEngine:
    """Advance the world season-by-season with deterministic snapshots."""

    def __init__(
        self,
        timeline_id: str = "main",
        rng_seed: int = 0,
        world_state: Optional[Dict[str, Any]] = None,
        base_path: str | Path = Path("src") / "save" / "saves",
        season_processors: Optional[
            List[Callable[["TimeEngine", TimePosition, random.Random], None]]
        ] = None,
    ) -> None:
        self.timeline_id = timeline_id
        self.rng_seed = rng_seed
        self.world_state: Dict[str, Any] = copy.deepcopy(world_state) if world_state is not None else {}
        self.store = SnapshotStore(Path(base_path) / "timelines", timeline_id)
        self.schema_version = SCHEMA_VERSION
        self.season_processors = season_processors or [self._run_weather]
        self._events: list[dict[str, Any]] = []
        self._dirty_from: TimePosition | None = None
        self._catch_up_target: TimePosition | None = None
        stored = self.store.load()
        if stored:
            self._load_from_dict(stored)
        else:
            self.current_position = TimePosition(0, 0)
            self.snapshots: list[dict[str, Any]] = []
            self._save_snapshot(self.current_position)

    # ------------------------------------------------------------------
    # Snapshot helpers
    # ------------------------------------------------------------------
    def _compress_state(self, state: dict[str, Any]) -> str:
        payload = json.dumps(state, ensure_ascii=False).encode("utf-8")
        compressed = gzip.compress(payload)
        return base64.b64encode(compressed).decode("ascii")

    def _decompress_state(self, blob: str) -> dict[str, Any]:
        raw = gzip.decompress(base64.b64decode(blob.encode("ascii")))
        return json.loads(raw.decode("utf-8"))

    def _state_checksum(self, state: dict[str, Any]) -> str:
        payload = json.dumps(state, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _save_snapshot(self, pos: TimePosition, meta: dict[str, Any] | None = None) -> None:
        snapshot_state = copy.deepcopy(self.world_state)
        compressed = self._compress_state(snapshot_state)
        entry = {
            "schema_version": self.schema_version,
            "timeline_id": self.timeline_id,
            "year": pos.year,
            "season": pos.season,
            "state_blob": compressed,
            "checksum": self._state_checksum(snapshot_state),
            "events": list(self._events),
        }
        if meta:
            entry["meta"] = meta
        self.snapshots.append(entry)
        self._persist()

    def _persist(self) -> None:
        payload = {
            "schema_version": self.schema_version,
            "timeline_id": self.timeline_id,
            "rng_seed": self.rng_seed,
            "snapshots": self.snapshots,
        }
        self.store.save(payload)

    def _load_from_dict(self, data: dict[str, Any]) -> None:
        self.schema_version = data.get("schema_version", SCHEMA_VERSION)
        self.timeline_id = data.get("timeline_id", self.timeline_id)
        self.rng_seed = data.get("rng_seed", self.rng_seed)
        self.snapshots = data.get("snapshots", [])
        if self.snapshots:
            last = self.snapshots[-1]
            self.world_state = self._decompress_state(last.get("state_blob", ""))
            self.current_position = TimePosition.from_season(
                last.get("year", 0), last.get("season", "spring")
            )
        else:
            self.current_position = TimePosition(0, 0)

    def _nearest_snapshot(self, target: TimePosition) -> dict[str, Any] | None:
        candidates = [s for s in self.snapshots if self._pos_from_snapshot(s) <= target]
        if not candidates:
            return None
        return candidates[-1]

    def _pos_from_snapshot(self, snap: dict[str, Any]) -> TimePosition:
        return TimePosition.from_season(int(snap.get("year", 0)), snap.get("season", "spring"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def reset_timeline(
        self,
        world_state: Optional[Dict[str, Any]] = None,
        rng_seed: Optional[int] = None,
        timeline_id: Optional[str] = None,
    ) -> None:
        """Clear existing data and start a new timeline."""

        if world_state is not None:
            self.world_state = copy.deepcopy(world_state)
        else:
            self.world_state = {}
        if rng_seed is not None:
            self.rng_seed = rng_seed
        if timeline_id is not None:
            self.timeline_id = timeline_id
            self.store = SnapshotStore(self.store.base_path, self.timeline_id)
        self.current_position = TimePosition(0, 0)
        self.snapshots = []
        self._events = []
        self._dirty_from = None
        self._catch_up_target = None
        self._save_snapshot(self.current_position)

    def events_for_position(self, pos: TimePosition) -> list[dict[str, Any]]:
        for snap in self.snapshots:
            if self._pos_from_snapshot(snap) == pos:
                return list(snap.get("events", []))
        return []

    def step_seasons(self, delta: int) -> TimePosition:
        target = self.current_position.step(delta)
        return self.step_to(target)

    def step_to(self, target: TimePosition) -> TimePosition:
        if target == self.current_position:
            return target
        if target < self.current_position:
            self._restore_to(target)
            return self.current_position
        # forward play with auto-generation
        while self.current_position < target:
            self._advance_one_season()
        return self.current_position

    # ------------------------------------------------------------------
    # Season processing
    # ------------------------------------------------------------------
    def _advance_one_season(self) -> None:
        next_pos = self.current_position.step(1)
        self._events = []
        rng = rng_for(
            timeline_id=self.timeline_id,
            year=next_pos.year,
            season=next_pos.season,
            node_id=None,
            subsystem_tag="season",
            base_seed=self.rng_seed,
        )
        for processor in self.season_processors:
            processor(self, next_pos, rng)
        self.current_position = next_pos
        self._save_snapshot(self.current_position)
        if self._catch_up_target and self.current_position >= self._catch_up_target:
            self._dirty_from = None
            self._catch_up_target = None

    def _run_weather(self, engine: "TimeEngine", pos: TimePosition, rng: random.Random) -> None:
        total, weather_type = roll_weather(pos.season, rng=rng)
        result = {
            "type": "weather_roll",
            "year": pos.year,
            "season": pos.season,
            "total": total,
            "name": weather_type.name,
        }
        self._events.append(result)
        self.world_state.setdefault("weather_history", []).append(result)

    def _restore_to(self, target: TimePosition) -> None:
        snap = self._nearest_snapshot(target)
        if snap is None:
            self.reset_timeline(self.world_state, self.rng_seed, self.timeline_id)
            return
        self.world_state = self._decompress_state(snap.get("state_blob", ""))
        self.current_position = self._pos_from_snapshot(snap)
        self._events = list(snap.get("events", []))
        if self.current_position < target:
            while self.current_position < target:
                self._advance_one_season()

    # ------------------------------------------------------------------
    # History management
    # ------------------------------------------------------------------
    def _truncate_future(self, pivot: TimePosition) -> None:
        """Remove snapshots at or after ``pivot`` to force recalculation."""

        kept: list[dict[str, Any]] = []
        for snap in self.snapshots:
            if self._pos_from_snapshot(snap) < pivot:
                kept.append(snap)
        self.snapshots = kept

    def record_change(self, reason: str | None = None) -> None:
        """Create a snapshot for a domain change at the current position.

        If the change happens in the past relative to the furthest generated
        snapshot the future gets marked as dirty and will be regenerated as the
        timeline advances.
        """

        if self.snapshots:
            previous_max = self._pos_from_snapshot(self.snapshots[-1])
        else:
            previous_max = self.current_position
        if self.current_position < previous_max:
            earliest_dirty = self._dirty_from or self.current_position
            self._dirty_from = min(earliest_dirty, self.current_position)
            self._catch_up_target = previous_max
        self._truncate_future(self.current_position)
        meta = {"reason": reason} if reason is not None else None
        self._save_snapshot(self.current_position, meta=meta)

    @property
    def future_dirty(self) -> bool:
        return self._catch_up_target is not None

    @property
    def catch_up_target(self) -> TimePosition | None:
        return self._catch_up_target

    def allows_decade_jumps(self) -> bool:
        """Return True if 10-year jumps are currently allowed."""

        if self._catch_up_target is None:
            return True
        return self.current_position >= self._catch_up_target


