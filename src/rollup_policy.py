"""Domain policy for values contributed to recursive rollups."""

from typing import Any, Mapping

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
