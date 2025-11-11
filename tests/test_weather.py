from unittest.mock import patch

from utils import available_resource_types
from weather import roll_weather


def test_available_resource_types_excludes_weather():
    world = {"nodes": {"1": {"node_id": 1, "res_type": "Väder"}}}
    opts = available_resource_types(world, current_node_id=2)
    assert "Väder" not in opts
    opts_current = available_resource_types(world, current_node_id=1)
    assert "Väder" in opts_current


def test_available_resource_types_hides_noble_family_before_depth_five():
    world = {"nodes": {}}
    opts = available_resource_types(world, current_node_id=None, depth=4)
    assert "Adelsfamilj" not in opts


def test_available_resource_types_allows_noble_family_at_depth_five():
    world = {"nodes": {}}
    opts = available_resource_types(world, current_node_id=None, depth=5)
    assert "Adelsfamilj" in opts


def test_roll_weather_table():
    with patch("random.randint", side_effect=[1, 1]):
        total, w = roll_weather("spring", modifier=-2)
    assert total == 0
    assert w.name == "Storm och hagel (+3)"

    with patch("random.randint", side_effect=[6, 6]):
        total, w = roll_weather("spring")
    assert total == 12
    assert w.name == "God växtkraft (-2)"

    with patch("random.randint", side_effect=[6, 6]):
        total, w = roll_weather("spring", modifier=2)
    assert total == 14
    assert w.name == "Exceptionellt vårväder (-3)"
