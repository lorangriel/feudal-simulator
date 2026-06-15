"""Domain policy for values contributed to recursive rollups."""

from typing import Any, Mapping

from constants import (
    DAGSVERKEN_MULTIPLIERS,
    DAY_LABORER_WORK_DAYS,
    THRALL_WORK_DAYS,
)

POPULATION_CATEGORIES = (
    "free_peasants",
    "unfree_peasants",
    "thralls",
    "burghers",
)


def _non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def get_local_population_contribution(node: Mapping[str, Any]) -> int:
    """Return only population originating on this node."""
    if any(category in node for category in POPULATION_CATEGORIES):
        return sum(
            _non_negative_int(node.get(category)) for category in POPULATION_CATEGORIES
        )

    if "_base_population" in node:
        return _non_negative_int(node.get("_base_population"))

    if node.get("children"):
        return 0

    level = node.get("level", node.get("depth"))
    if level is not None and _non_negative_int(level) <= 3:
        return 0

    return _non_negative_int(node.get("population"))


def get_local_work_needed_contribution(
    node: Mapping[str, Any], *, depth: int | None = None
) -> int:
    """Return only work need originating on this node."""
    if node.get("res_type") in {"Hav", "Flod"}:
        return _non_negative_int(node.get("fishing_boats")) * THRALL_WORK_DAYS

    node_depth = depth
    if node_depth is None:
        node_depth = node.get("level", node.get("depth"))

    try:
        resolved_depth = int(node_depth)
    except (TypeError, ValueError):
        return 0

    if resolved_depth <= 3:
        return 0

    return _non_negative_int(node.get("work_needed"))


def get_local_work_available_contribution(
    node: Mapping[str, Any],
    *,
    depth: int | None = None,
) -> int:
    """Return work capacity explicitly originating on this node."""
    del depth
    dagsverken = node.get("dagsverken", "normalt")
    multiplier = DAGSVERKEN_MULTIPLIERS.get(
        dagsverken, DAGSVERKEN_MULTIPLIERS["normalt"]
    )
    return (
        _non_negative_int(node.get("thralls")) * THRALL_WORK_DAYS
        + _non_negative_int(node.get("unfree_peasants")) * multiplier
        + _non_negative_int(node.get("day_laborers_hired")) * DAY_LABORER_WORK_DAYS
    )
