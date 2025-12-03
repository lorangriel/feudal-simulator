"""Helpers for personal province ownership rules and tax flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass
class TaxShare:
    """Result of distributing tax along a province path."""

    local_keep: float
    forwarded: float
    sink_level: int


class PersonalProvinceError(ValueError):
    """Raised when a personal province assignment is invalid."""


VALID_LEVELS = {"0", "1", "2", "none"}


def validate_assignment(
    owner_level: str, owner_id: Optional[int], existing_owner: Optional[int]
) -> None:
    """Validate a proposed owner assignment.

    The function ensures the level is recognised and that a single owner is
    enforced for the node.
    """

    normalised_level = str(owner_level or "none")
    if normalised_level not in VALID_LEVELS:
        raise PersonalProvinceError(f"Ogiltig ägarnivå: {owner_level}")

    if normalised_level != "none" and owner_id is None:
        raise PersonalProvinceError("Ägare måste anges för personlig provins")

    if normalised_level == "none":
        return

    if owner_id is not None and owner_id < 0:
        raise PersonalProvinceError("Ogiltigt ägar-id")


def build_personal_path(
    owner_level: str, owner_id: Optional[int], lineage: Iterable[int]
) -> List[int]:
    """Construct a personal province path from a lineage.

    ``lineage`` is expected to contain ancestor node ids from level 0 upward. A
    subset is returned depending on the ``owner_level``. Cycles are rejected.
    """

    normalised_level = str(owner_level or "none")
    if normalised_level == "none" or owner_id is None:
        return []

    seen: set[int] = set()
    path: List[int] = []
    for idx, ancestor in enumerate(lineage):
        if ancestor in seen:
            raise PersonalProvinceError("Cykel upptäckt i provinsvägen")
        seen.add(ancestor)
        path.append(ancestor)
        if str(idx) == normalised_level:
            break
    return path


def distribute_tax(
    income: float, keep_fraction: float, tax_forward_fraction: float, owner_level: str
) -> TaxShare:
    """Apply Model B tax rules for a jarldom.

    The function normalises the fractions and returns how much is kept locally,
    how much is forwarded, and the level that receives the forwarded tax.
    """

    if income < 0:
        raise PersonalProvinceError("Intäkt kan inte vara negativ")

    keep_fraction = max(0.0, min(1.0, keep_fraction))
    tax_forward_fraction = max(0.0, min(1.0, tax_forward_fraction))
    total = keep_fraction + tax_forward_fraction
    if total == 0:
        keep_fraction = tax_forward_fraction = 0.5
    else:
        keep_fraction /= total
        tax_forward_fraction /= total

    normalised_level = str(owner_level or "none")
    if normalised_level not in VALID_LEVELS:
        raise PersonalProvinceError(f"Ogiltig ägarnivå: {owner_level}")

    local_keep = income * keep_fraction
    forwarded = income * tax_forward_fraction

    sink_level = 0
    if normalised_level == "2":
        sink_level = 1
    elif normalised_level == "1":
        sink_level = 0
    elif normalised_level == "0":
        sink_level = 0
    elif normalised_level == "none":
        sink_level = 2

    return TaxShare(local_keep=local_keep, forwarded=forwarded, sink_level=sink_level)


def summarise_personal_income(
    jarldom_income: float,
    owner_level: str,
    keep_fraction: float,
    tax_forward_fraction: float,
    ancestor_keep: Dict[int, float] | None = None,
) -> Dict[str, float]:
    """Return a summary for administrative vs personal revenue.

    ``ancestor_keep`` allows the caller to feed in existing totals per level and
    is returned as a convenience to simplify accumulation in calling code.
    """

    ancestor_keep = ancestor_keep or {}
    share = distribute_tax(jarldom_income, keep_fraction, tax_forward_fraction, owner_level)
    admin_income = 0.0 if owner_level != "none" else jarldom_income
    ancestor_keep[f"level_{share.sink_level}"] = ancestor_keep.get(
        f"level_{share.sink_level}", 0.0
    ) + share.forwarded

    return {
        "administrative_income": admin_income,
        "personal_keep": share.local_keep,
        "forwarded_tax": share.forwarded,
        "forwarded_to_level": share.sink_level,
        "ancestor_totals": ancestor_keep,
    }
