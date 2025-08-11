import pytest

from src import population_utils as pu


def test_missing_fields_return_zero():
    assert pu.calculate_population_from_fields({}) == 0


def test_invalid_values_use_population_fallback():
    data = {
        "free_peasants": "bad",
        "unfree_peasants": "1",
        "thralls": "bad",
        "burghers": "bad",
        "population": "5",
    }
    assert pu.calculate_population_from_fields(data) == 5


def test_invalid_population_returns_zero():
    assert pu.calculate_population_from_fields({"population": "bad"}) == 0


def test_non_dict_input_raises():
    with pytest.raises(AttributeError):
        pu.calculate_population_from_fields(None)


def test_negative_values_are_summed_when_nonzero():
    data = {
        "free_peasants": "-5",
        "unfree_peasants": "3",
        "thralls": "2",
        "burghers": "1",
    }
    assert pu.calculate_population_from_fields(data) == 1
