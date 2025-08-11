"""Utility functions related to population calculations."""

from __future__ import annotations


def calculate_population_from_fields(data: dict) -> int:
    """Compute total population from category fields.

    The function sums specific population categories. If the total of
    those categories is zero, it falls back to the ``population`` field.
    All non-numeric values are treated as zero.

    Parameters
    ----------
    data:
        Mapping containing population information.

    Returns
    -------
    int
        The computed total population.
    """

    try:
        free_p = int(data.get("free_peasants", 0) or 0)
        unfree_p = int(data.get("unfree_peasants", 0) or 0)
        thralls = int(data.get("thralls", 0) or 0)
        burghers = int(data.get("burghers", 0) or 0)
    except (ValueError, TypeError):
        free_p = unfree_p = thralls = burghers = 0

    total = free_p + unfree_p + thralls + burghers
    if total:
        return total

    try:
        return int(data.get("population", 0) or 0)
    except (ValueError, TypeError):
        return 0
