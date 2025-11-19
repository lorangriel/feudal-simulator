"""Utilities for calculating noble household staff requirements."""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any, Dict, Iterable, List, Mapping, Tuple


@dataclass(frozen=True)
class NobleHousingTier:
    """Represents one mapping between standard, living level and housing."""

    standard: str
    living_level: str
    building_type: str


NOBLE_HOUSING_TIERS: Tuple[NobleHousingTier, ...] = (
    NobleHousingTier("Enkel", "Nödtorftig", "Trästuga liten"),
    NobleHousingTier("Anständig", "Gemen", "Trästuga 2 våningar"),
    NobleHousingTier("Välbärgad", "God", "Stenhus"),
    NobleHousingTier("Förnäm", "Mycket god", "Borgkärna"),
    NobleHousingTier("Furstlig", "Lyxliv", "Sammansatt borgkärna"),
)

NOBLE_STANDARD_ORDER: Tuple[str, ...] = tuple(t.standard for t in NOBLE_HOUSING_TIERS)
NOBLE_BUILDING_ORDER: Tuple[str, ...] = tuple(t.building_type for t in NOBLE_HOUSING_TIERS)
_STANDARD_RANK: Dict[str, int] = {standard: idx for idx, standard in enumerate(NOBLE_STANDARD_ORDER)}
_BUILDING_RANK: Dict[str, int] = {building: idx for idx, building in enumerate(NOBLE_BUILDING_ORDER)}

# Mapping from noble standard keys used in the UI to the living levels
# referenced by the staff requirement tables.
STANDARD_TO_LIVING_LEVEL: Dict[str, str] = {
    tier.standard: tier.living_level for tier in NOBLE_HOUSING_TIERS
}

# Housing requirement descriptions per living level.
HOUSING_REQUIREMENTS: Dict[str, str] = {
    tier.living_level: tier.building_type for tier in NOBLE_HOUSING_TIERS
}


def get_standard_rank(standard_key: str | None) -> int:
    """Return the ordinal rank for a noble standard or ``-1`` if unknown."""

    if not standard_key:
        return -1
    return _STANDARD_RANK.get(standard_key, -1)


def get_allowed_standards_for_rank(rank: int) -> Tuple[str, ...]:
    """Return standards allowed up to ``rank`` (inclusive)."""

    if rank < 0:
        return ()
    limit = min(rank + 1, len(NOBLE_STANDARD_ORDER))
    return NOBLE_STANDARD_ORDER[:limit]


def get_highest_building_rank(
    buildings: Iterable[Mapping[str, Any]] | None,
) -> int:
    """Return the highest building rank present in ``buildings``."""

    max_rank = -1
    if not buildings:
        return max_rank
    for entry in buildings:
        if not isinstance(entry, Mapping):
            continue
        btype = entry.get("type")
        if not btype:
            continue
        try:
            count = int(entry.get("count", 0) or 0)
        except (TypeError, ValueError):
            continue
        if count <= 0:
            continue
        rank = _BUILDING_RANK.get(str(btype))
        if rank is not None and rank > max_rank:
            max_rank = rank
    return max_rank


def get_max_allowed_standard_for_buildings(
    buildings: Iterable[Mapping[str, Any]] | None,
) -> str | None:
    """Return the highest standard supported by ``buildings`` if any."""

    rank = get_highest_building_rank(buildings)
    if rank < 0:
        return None
    return NOBLE_STANDARD_ORDER[rank]


def get_allowed_standards_for_buildings(
    buildings: Iterable[Mapping[str, Any]] | None,
) -> Tuple[str, ...]:
    """Return all standards supported by ``buildings``."""

    return get_allowed_standards_for_rank(get_highest_building_rank(buildings))

# Display order for staff roles in the UI.
STAFF_ROLE_ORDER: Tuple[str, ...] = (
    "Kammarherre",
    "Hovmästare",
    "Köksmästare",
    "Kock",
    "Kammarjungfru",
    "Kallskänka",
    "Kokerka",
    "Tjänare",
    "Hushållspersonal",
)

ROLE_DESCRIPTIONS: Dict[str, str] = {
    "Kammarherre": (
        "Hushållets ekonomiska och administrativa chef. Sköter räkenskaper, "
        "inköp, egendomsförvaltning och övervakning av personal."
    ),
    "Hovmästare": (
        "Leder tjänarna och ansvarar för ordning, servering och gästbemötande. "
        "Representerar hushållet och organiserar större tillställningar."
    ),
    "Köksmästare": (
        "Kökschef som planerar menyer, väljer råvaror och övervakar kockar och "
        "servering."
    ),
    "Kock": (
        "Professionell matlagare. Sköter huvudrätter och festmåltider. I större "
        "hushåll arbetar han under köksmästaren."
    ),
    "Kammarjungfru": (
        "Personlig tjänare åt länsherrens familj. Ansvarar för kläder, frisyr, "
        "toalett, resor och diskreta tjänster. Motsvarighet i herrhushåll: valet."
    ),
    "Kallskänka": (
        "Ansvarar för kalla rätter, bröd, bakverk, uppläggning, servering och i "
        "större hushåll även förvaring, sylter och bakhus."
    ),
    "Kokerka": (
        "Arbetar i köket med enkla sysslor: disk, vatten, ved, rengöring, "
        "råvaruförberedelser och enklare matlagning."
    ),
    "Tjänare": (
        "Frontpersonal som serverar, bär, öppnar dörrar, följer med på resor och "
        "hjälper gäster. Vid högre nivåer bär de livré och ansvarar för etikett."
    ),
    "Hushållspersonal": (
        "Städ, tvätt, eldning, bäddning och enklare underhåll. Ansvarar för att "
        "hushållet fungerar dagligen."
    ),
}

# Base and luxury level costs per role (per year).
_ROLE_COST_BASE: Dict[str, int] = {
    "Kammarherre": 2,
    "Hovmästare": 2,
    "Köksmästare": 2,
    "Kock": 3,
    "Kammarjungfru": 3,
    "Kallskänka": 2,
    "Kokerka": 2,
    "Tjänare": 2,
    "Hushållspersonal": 1,
}

_ROLE_COST_LYX: Dict[str, int] = {
    "Kammarherre": 2,
    "Hovmästare": 2,
    "Köksmästare": 1,
}


def get_living_level_for_standard(standard_key: str | None) -> str:
    """Return the living level for a noble standard key."""

    if not standard_key:
        return "God"
    return STANDARD_TO_LIVING_LEVEL.get(standard_key, "God")


def get_housing_requirement_for_level(living_level: str) -> str:
    """Return the housing requirement text for the provided living level."""

    return HOUSING_REQUIREMENTS.get(living_level, "")


def _round_half_up(value: float) -> int:
    """Round positive values using half-up semantics."""

    if value >= 0:
        return int(value + 0.5)
    return int(value - 0.5)


def _entry_counts_as_person(entry: object) -> bool:
    """Determine whether a stored entry represents a household member."""

    if entry is None:
        return False
    if isinstance(entry, dict):
        kind = entry.get("kind")
        if kind == "character":
            try:
                int(entry.get("char_id"))
            except (TypeError, ValueError):
                return False
            return True
        if kind == "placeholder":
            label = entry.get("label", "")
            return bool(str(label).strip())
        return False
    if isinstance(entry, (int, float)):
        return True
    if isinstance(entry, str):
        return bool(entry.strip())
    return False


def _count_entries(entries: Iterable[object]) -> int:
    return sum(1 for entry in entries if _entry_counts_as_person(entry))


@dataclass(frozen=True)
class NobleHouseholdSummary:
    """Aggregated counts of noble household members."""

    lord: int
    spouses: int
    children: int
    relatives: int

    @property
    def total(self) -> int:
        return self.lord + self.spouses + self.children + self.relatives


def _flatten_children(children_data: object) -> List[object]:
    if not isinstance(children_data, list):
        return []
    flat: List[object] = []
    for item in children_data:
        if isinstance(item, list):
            flat.extend(item)
        else:
            flat.append(item)
    return flat


def calculate_noble_household(node_data: Dict[str, object]) -> NobleHouseholdSummary:
    """Calculate the noble household composition for a node."""

    lord = 1 if _entry_counts_as_person(node_data.get("noble_lord")) else 0

    spouses_data = node_data.get("noble_spouses")
    if isinstance(spouses_data, list):
        spouses = _count_entries(spouses_data)
    else:
        spouses = 1 if _entry_counts_as_person(spouses_data) else 0

    spouse_children_raw = node_data.get("noble_spouse_children")
    children_entries = _flatten_children(spouse_children_raw)
    if not children_entries:
        children_entries = node_data.get("noble_children") or []
        if not isinstance(children_entries, list):
            children_entries = [children_entries]
    children = _count_entries(children_entries)

    relatives_data = node_data.get("noble_relatives")
    if isinstance(relatives_data, list):
        relatives = _count_entries(relatives_data)
    else:
        relatives = 1 if _entry_counts_as_person(relatives_data) else 0

    return NobleHouseholdSummary(lord=lord, spouses=spouses, children=children, relatives=relatives)


def _role_cost(role: str, living_level: str) -> int:
    if living_level == "Lyxliv":
        if role in _ROLE_COST_LYX:
            return _ROLE_COST_LYX[role]
    return _ROLE_COST_BASE.get(role, 0)


StaffCounts = Dict[str, int]
RoleCostSummary = Dict[str, Tuple[int, int]]
RoleCostTotals = Dict[str, Tuple[int, int | None]]


def calculate_staff_requirements(living_level: str, nobles_count: int) -> StaffCounts:
    """Calculate required staff counts for a given living level and household size."""

    nobles = max(0, int(nobles_count))
    counts: StaffCounts = {role: 0 for role in STAFF_ROLE_ORDER}

    if living_level == "Nödtorftig":
        counts["Kokerka"] = max(1, ceil(nobles / 15))
        counts["Tjänare"] = max(1, ceil(nobles / 20))
        counts["Hushållspersonal"] = max(1, ceil(nobles / 8))
    elif living_level == "Gemen":
        counts["Kokerka"] = max(1, ceil(nobles / 10))
        counts["Tjänare"] = max(1, ceil(nobles / 15))
        counts["Hushållspersonal"] = max(1, ceil(nobles / 8))
        counts["Kallskänka"] = max(1, ceil(nobles / 12))
    elif living_level == "Mycket god":
        t_count = max(1, ceil(3 + 1 * nobles))
        counts["Kammarjungfru"] = max(0, _round_half_up(0.4 * nobles + 1))
        counts["Kallskänka"] = max(0, _round_half_up(0.3 * nobles + 1))
        counts["Kokerka"] = max(1, ceil(1 + 0.6 * nobles))
        counts["Tjänare"] = t_count
        counts["Hushållspersonal"] = max(1, ceil(t_count + 4))
        counts["Kock"] = 1
        counts["Kammarherre"] = 1
        counts["Hovmästare"] = 1
    elif living_level == "Lyxliv":
        t_count = max(1, ceil(3 + 2 * nobles))
        counts["Kammarjungfru"] = max(0, _round_half_up(0.8 * nobles + 1))
        counts["Kallskänka"] = max(0, _round_half_up(0.5 * nobles + 1))
        counts["Kokerka"] = max(1, ceil(1 + 0.7 * nobles))
        counts["Tjänare"] = t_count
        counts["Hushållspersonal"] = max(1, ceil(t_count + 7))
        counts["Kock"] = 1
        counts["Kammarherre"] = 1
        counts["Hovmästare"] = 1
        counts["Köksmästare"] = 1
    else:  # Default to "God" level
        t_count = max(1, ceil(3 + 0.5 * nobles))
        counts["Kokerka"] = max(1, ceil(1 + 0.5 * nobles))
        counts["Tjänare"] = t_count
        counts["Hushållspersonal"] = max(1, ceil(t_count + 2))
        counts["Kallskänka"] = max(0, _round_half_up(0.3 * nobles + 1))
        counts["Kammarjungfru"] = max(0, _round_half_up(0.3 * nobles + 1))
        counts["Kock"] = 1
        counts["Kammarherre"] = 1

    return counts


def calculate_staff_costs(counts: StaffCounts, living_level: str) -> Tuple[RoleCostSummary, int]:
    """Calculate total and per-role staff costs."""

    per_role: RoleCostSummary = {}
    total = 0
    for role, count in counts.items():
        if count <= 0:
            continue
        unit_cost = _role_cost(role, living_level)
        role_total = unit_cost * count
        per_role[role] = (unit_cost, role_total)
        total += role_total
    return per_role, total


def get_role_costs(role: str) -> Tuple[int, int | None]:
    """Return the base and lyx per-person cost for a role."""

    return _ROLE_COST_BASE.get(role, 0), _ROLE_COST_LYX.get(role)


def calculate_staff_cost_totals(
    counts: StaffCounts,
) -> Tuple[RoleCostTotals, int, int]:
    """Calculate base and lyx totals for each role and overall sums."""

    per_role: RoleCostTotals = {}
    base_total = 0
    lyx_total = 0
    for role, count in counts.items():
        if count <= 0:
            continue
        base_cost, lyx_cost = get_role_costs(role)
        role_base_total = base_cost * count
        role_lyx_total: int | None
        if lyx_cost is None:
            role_lyx_total = None
        else:
            role_lyx_total = lyx_cost * count
            lyx_total += role_lyx_total
        per_role[role] = (role_base_total, role_lyx_total)
        base_total += role_base_total
    return per_role, base_total, lyx_total
