import math

import pytest

from personal_province import (
    PersonalProvinceError,
    build_personal_path,
    distribute_tax,
    summarise_personal_income,
    validate_assignment,
)


def test_validate_assignment_rejects_unknown_level():
    with pytest.raises(PersonalProvinceError):
        validate_assignment("3", 1, None)


def test_validate_assignment_requires_owner_for_personal():
    with pytest.raises(PersonalProvinceError):
        validate_assignment("1", None, None)


@pytest.mark.parametrize(
    "owner_level,expected",
    [("none", []), ("1", [10, 11]), ("2", [10, 11, 12])],
)
def test_build_personal_path(owner_level, expected):
    lineage = [10, 11, 12, 13]
    assert build_personal_path(owner_level, 99, lineage) == expected


def test_build_personal_path_detects_cycle():
    with pytest.raises(PersonalProvinceError):
        build_personal_path("2", 3, [1, 2, 1])


@pytest.mark.parametrize(
    "keep_fraction,tax_fraction",
    [(0.5, 0.5), (0.0, 1.0), (1.0, 0.0), (0.25, 0.75)],
)
def test_distribute_tax_normalises(keep_fraction, tax_fraction):
    share = distribute_tax(100, keep_fraction, tax_fraction, "2")
    assert math.isclose(share.local_keep + share.forwarded, 100)
    assert share.sink_level == 1


@pytest.mark.parametrize(
    "owner_level,expected_sink",
    [("2", 1), ("1", 0), ("0", 0), ("none", 2)],
)
def test_distribute_tax_sink_levels(owner_level, expected_sink):
    share = distribute_tax(50, 0.5, 0.5, owner_level)
    assert share.sink_level == expected_sink


def test_summarise_personal_income_updates_ancestors():
    summary = summarise_personal_income(120, "2", 0.5, 0.5)
    assert math.isclose(summary["personal_keep"], 60)
    assert math.isclose(summary["forwarded_tax"], 60)
    assert summary["ancestor_totals"]["level_1"] == pytest.approx(60)
    assert summary["administrative_income"] == 0.0
