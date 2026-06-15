"""Read-only presentation helpers for explicit world relations."""

from collections.abc import Callable, Mapping
from typing import Any

import world_relations

_WARNING_LABELS = {
    "title_missing_seat": "Titeln saknar angivet säte.",
    "duplicate_title_seat": ("Jarldömet används redan som säte för en annan titel."),
    "seat_outside_title_subtree": "Sätet ligger utanför titelns område.",
    "unknown_seat_node": "Det angivna sätet finns inte längre.",
    "seat_not_jarldom": "Det angivna sätet är inte ett jarldöme.",
    "unknown_title_node": "Titeln finns inte längre.",
    "seat_source_not_title": "Noden är inte en titel som kan ha säte.",
    "jarldom_missing_owner": "Jarldömet saknar angiven ägare.",
    "unknown_owner_character": ("Den angivna ägarkaraktären finns inte längre."),
    "unknown_owner_jarldom": "Jarldömet finns inte längre.",
    "owner_key_not_jarldom": ("Ägarrelationen pekar inte på ett jarldöme."),
}


def _as_id(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _get_node(world_data: Any, node_id: Any) -> Mapping[str, Any]:
    if not isinstance(world_data, Mapping):
        return {}
    nodes = world_data.get("nodes")
    if not isinstance(nodes, Mapping):
        return {}
    wanted_id = _as_id(node_id)
    for raw_id, node in nodes.items():
        candidate_id = _as_id(raw_id)
        if candidate_id is None and isinstance(node, Mapping):
            candidate_id = _as_id(node.get("node_id"))
        if candidate_id == wanted_id and isinstance(node, Mapping):
            return node
    return {}


def _format_target(
    target_id: int,
    label_callback: Callable[[int], str] | None,
    fallback_kind: str,
) -> str:
    label = (
        str(label_callback(target_id)).strip()
        if label_callback is not None
        else f"{fallback_kind} {target_id}"
    )
    if not label:
        label = f"{fallback_kind} {target_id}"
    if f"ID {target_id}" in label:
        return label
    return f"{label} (ID {target_id})"


def _row(
    key: str,
    label: str,
    target_id: int | None,
    missing_value: str,
    label_callback: Callable[[int], str] | None,
    fallback_kind: str,
) -> dict:
    return {
        "key": key,
        "label": label,
        "value": (
            _format_target(target_id, label_callback, fallback_kind)
            if target_id is not None
            else missing_value
        ),
        "target_id": target_id,
        "status": "ok" if target_id is not None else "missing",
    }


def _warning(issue: Any) -> dict:
    code = getattr(issue, "code", "")
    return {
        "code": code,
        "label": _WARNING_LABELS.get(code, "Okänt relationsproblem."),
        "source_id": getattr(issue, "source_id", None),
        "target_id": getattr(issue, "target_id", None),
    }


def _title_warnings(
    world_data: Any, title_id: Any, seat_id: int | None
) -> tuple[dict, ...]:
    wanted_id = _as_id(title_id)
    return tuple(
        _warning(issue)
        for issue in world_relations.validate_world_relations(world_data, strict=True)
        if getattr(issue, "source_id", None) == wanted_id
        or (
            seat_id is not None
            and getattr(issue, "target_id", None) == seat_id
            and getattr(issue, "code", "").startswith(("seat_", "duplicate_title_seat"))
        )
    )


def _jarldom_warnings(
    world_data: Any, jarldom_id: Any, owner_id: int | None
) -> tuple[dict, ...]:
    wanted_id = _as_id(jarldom_id)
    return tuple(
        _warning(issue)
        for issue in world_relations.validate_world_relations(world_data, strict=True)
        if getattr(issue, "source_id", None) == wanted_id
        or getattr(issue, "target_id", None) == wanted_id
        or (
            owner_id is not None
            and getattr(issue, "target_id", None) == owner_id
            and getattr(issue, "code", "") == "unknown_owner_character"
        )
    )


def build_title_relations_presentation(
    world_data: Any,
    title_id: Any,
    *,
    get_node_label: Callable[[int], str] | None = None,
) -> dict:
    """Build read-only presentation data for a level 0-2 title node."""
    seat_id = world_relations.get_title_seat(world_data, title_id)
    return {
        "title": "Relationer",
        "rows": (
            _row(
                "title_seat",
                "Titelns säte",
                seat_id,
                "Inget säte angivet",
                get_node_label,
                "Nod",
            ),
        ),
        "warnings": _title_warnings(world_data, title_id, seat_id),
    }


def build_jarldom_relations_presentation(
    world_data: Any,
    jarldom_id: Any,
    *,
    get_node_label: Callable[[int], str] | None = None,
    get_character_label: Callable[[int], str] | None = None,
) -> dict:
    """Build read-only presentation data for a level 3 jarldom node."""
    node = _get_node(world_data, jarldom_id)
    owner_id = world_relations.get_jarldom_owner(world_data, jarldom_id)
    ruler_id = _as_id(node.get("ruler_id"))
    anchor_id = _as_id(node.get("owner_assigned_id"))
    seated_title_id = world_relations.get_seated_title(world_data, jarldom_id)
    return {
        "title": "Relationer",
        "rows": (
            _row(
                "jarldom_owner",
                "Jarldömets ägare",
                owner_id,
                "Ingen ägare angiven",
                get_character_label,
                "Karaktär",
            ),
            _row(
                "ruler",
                "Härskare",
                ruler_id,
                "Ingen härskare angiven",
                get_character_label,
                "Karaktär",
            ),
            _row(
                "personal_province_anchor",
                "Personlig provins / titelankare",
                anchor_id,
                "Lokal, inget titelankare",
                get_node_label,
                "Nod",
            ),
            _row(
                "seat_for_title",
                "Säte för titel",
                seated_title_id,
                "Inte säte för någon titel",
                get_node_label,
                "Nod",
            ),
        ),
        "warnings": _jarldom_warnings(world_data, jarldom_id, owner_id),
    }
