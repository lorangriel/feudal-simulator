"""Read-only access to explicit title-seat and jarldom-owner relations."""

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Set


@dataclass(frozen=True)
class RelationIssue:
    """A machine-readable problem with an explicit world relation."""

    code: str
    source_id: Optional[int] = None
    target_id: Optional[int] = None
    message: str = ""


def _as_id(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = value.strip()
        if value and value.isdigit():
            return int(value)
    return None


def _mapping(world_data: Any, key: str) -> Mapping[Any, Any]:
    if not isinstance(world_data, Mapping):
        return {}
    value = world_data.get(key)
    return value if isinstance(value, Mapping) else {}


def _nodes(world_data: Any) -> Dict[int, Mapping[str, Any]]:
    result = {}
    for raw_id, node in _mapping(world_data, "nodes").items():
        node_id = _as_id(raw_id)
        if node_id is None and isinstance(node, Mapping):
            node_id = _as_id(node.get("node_id"))
        if node_id is not None and isinstance(node, Mapping):
            result[node_id] = node
    return result


def _node_depth(nodes: Mapping[int, Mapping[str, Any]], node_id: int) -> Optional[int]:
    depth = 0
    current_id = node_id
    visited = set()
    while current_id in nodes:
        if current_id in visited:
            return None
        visited.add(current_id)
        parent_id = _as_id(nodes[current_id].get("parent_id"))
        if parent_id is None:
            return depth
        if parent_id not in nodes:
            return None
        current_id = parent_id
        depth += 1
    return None  # pragma: no cover - loop exits through the checks above


def _is_descendant(
    nodes: Mapping[int, Mapping[str, Any]], node_id: int, ancestor_id: int
) -> bool:
    current_id = node_id
    visited = set()
    while current_id in nodes and current_id not in visited:
        visited.add(current_id)
        parent_id = _as_id(nodes[current_id].get("parent_id"))
        if parent_id == ancestor_id:
            return True
        if parent_id is None:
            return False
        current_id = parent_id
    return False  # pragma: no cover - guarded fallback for malformed mappings


def get_title_seat(world_data: Any, title_id: Any) -> Optional[int]:
    """Return the seat jarldom id for a title node, if explicitly configured."""
    wanted_id = _as_id(title_id)
    if wanted_id is None:
        return None
    for raw_title_id, raw_seat_id in _mapping(world_data, "title_seats").items():
        if _as_id(raw_title_id) == wanted_id:
            return _as_id(raw_seat_id)
    return None


def get_seated_title(world_data: Any, jarldom_id: Any) -> Optional[int]:
    """Return the unique title node id using this jarldom as its seat."""
    wanted_id = _as_id(jarldom_id)
    if wanted_id is None:
        return None
    title_ids = {
        title_id
        for raw_title_id, raw_seat_id in _mapping(world_data, "title_seats").items()
        if _as_id(raw_seat_id) == wanted_id
        if (title_id := _as_id(raw_title_id)) is not None
    }
    return next(iter(title_ids)) if len(title_ids) == 1 else None


def get_jarldom_owner(world_data: Any, jarldom_id: Any) -> Optional[int]:
    """Return the character id explicitly configured to own a jarldom."""
    wanted_id = _as_id(jarldom_id)
    if wanted_id is None:
        return None
    for raw_jarldom_id, raw_character_id in _mapping(
        world_data, "jarldom_owners"
    ).items():
        if _as_id(raw_jarldom_id) == wanted_id:
            return _as_id(raw_character_id)
    return None


def get_owned_jarldoms(world_data: Any, character_id: Any) -> List[int]:
    """Return sorted jarldom ids explicitly owned by the given character id."""
    wanted_id = _as_id(character_id)
    if wanted_id is None:
        return []
    jarldom_ids = {
        jarldom_id
        for raw_jarldom_id, raw_character_id in _mapping(
            world_data, "jarldom_owners"
        ).items()
        if _as_id(raw_character_id) == wanted_id
        if (jarldom_id := _as_id(raw_jarldom_id)) is not None
    }
    return sorted(jarldom_ids)


def _issue(
    code: str,
    source_id: Optional[int],
    target_id: Optional[int],
    message: str,
) -> RelationIssue:
    return RelationIssue(code, source_id, target_id, message)


def validate_world_relations(
    world_data: Any, strict: bool = False
) -> List[RelationIssue]:
    """Return structured relation issues without mutating world data."""
    nodes = _nodes(world_data)
    issues = []
    configured_titles: Set[int] = set()
    configured_jarldoms: Set[int] = set()
    seats_to_titles: Dict[int, List[int]] = {}

    for raw_title_id, raw_seat_id in _mapping(world_data, "title_seats").items():
        title_id = _as_id(raw_title_id)
        seat_id = _as_id(raw_seat_id)
        if title_id is not None:
            configured_titles.add(title_id)
        if title_id is None or title_id not in nodes:
            issues.append(
                _issue(
                    "unknown_title_node",
                    title_id,
                    seat_id,
                    "Title-seat source does not identify an existing node.",
                )
            )
        elif _node_depth(nodes, title_id) not in {0, 1, 2}:
            issues.append(
                _issue(
                    "seat_source_not_title",
                    title_id,
                    seat_id,
                    "Title-seat source is not a level 0-2 title.",
                )
            )

        if seat_id is None or seat_id not in nodes:
            issues.append(
                _issue(
                    "unknown_seat_node",
                    title_id,
                    seat_id,
                    "Configured seat does not identify an existing node.",
                )
            )
            continue
        seats_to_titles.setdefault(seat_id, []).append(title_id)
        if _node_depth(nodes, seat_id) != 3:
            issues.append(
                _issue(
                    "seat_not_jarldom",
                    title_id,
                    seat_id,
                    "Configured seat is not a level 3 jarldom.",
                )
            )
        elif (
            title_id is not None
            and title_id in nodes
            and not _is_descendant(nodes, seat_id, title_id)
        ):
            issues.append(
                _issue(
                    "seat_outside_title_subtree",
                    title_id,
                    seat_id,
                    "Configured seat is outside the title subtree.",
                )
            )

    for seat_id, title_ids in seats_to_titles.items():
        if len(title_ids) > 1:
            for title_id in title_ids:
                issues.append(
                    _issue(
                        "duplicate_title_seat",
                        title_id,
                        seat_id,
                        "Jarldom is configured as the seat of multiple titles.",
                    )
                )

    character_ids = {
        character_id
        for raw_id in _mapping(world_data, "characters")
        if (character_id := _as_id(raw_id)) is not None
    }
    for raw_jarldom_id, raw_character_id in _mapping(
        world_data, "jarldom_owners"
    ).items():
        jarldom_id = _as_id(raw_jarldom_id)
        character_id = _as_id(raw_character_id)
        if jarldom_id is not None:
            configured_jarldoms.add(jarldom_id)
        if jarldom_id is None or jarldom_id not in nodes:
            issues.append(
                _issue(
                    "unknown_owner_jarldom",
                    jarldom_id,
                    character_id,
                    "Owner source does not identify an existing node.",
                )
            )
        elif _node_depth(nodes, jarldom_id) != 3:
            issues.append(
                _issue(
                    "owner_key_not_jarldom",
                    jarldom_id,
                    character_id,
                    "Owner source is not a level 3 jarldom.",
                )
            )
        if character_id is None or character_id not in character_ids:
            issues.append(
                _issue(
                    "unknown_owner_character",
                    jarldom_id,
                    character_id,
                    "Owner target is not in the global character registry.",
                )
            )

    if strict:
        for node_id in sorted(nodes):
            depth = _node_depth(nodes, node_id)
            if depth in {0, 1, 2} and node_id not in configured_titles:
                issues.append(
                    _issue(
                        "title_missing_seat",
                        node_id,
                        None,
                        "Title has no explicitly configured seat.",
                    )
                )
            elif depth == 3 and node_id not in configured_jarldoms:
                issues.append(
                    _issue(
                        "jarldom_missing_owner",
                        node_id,
                        None,
                        "Jarldom has no explicitly configured owner.",
                    )
                )

    return issues
