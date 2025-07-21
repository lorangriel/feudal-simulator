import math
from src.map_logic import StaticMapLogic


def make_world():
    return {
        "nodes": {
            "10": {"node_id": 10, "neighbors": [{"id": 20, "border": "v\u00e4g"}]},
            "20": {"node_id": 20, "neighbors": [{"id": 10, "border": "v\u00e4g"}]},
            "30": {"node_id": 30, "neighbors": []},
        },
        "characters": {},
    }


def test_hex_center_calculation():
    logic = StaticMapLogic({}, rows=2, cols=2, hex_size=30, spacing=15)
    cx0, cy0 = logic.hex_center(0, 0)
    assert math.isclose(cx0, 50)
    assert math.isclose(cy0, 50)

    cx1, cy1 = logic.hex_center(1, 0)
    expected_cy1 = 50 + (30 * math.sqrt(3) + 15)
    assert math.isclose(cx1, 50)
    assert math.isclose(cy1, expected_cy1)

    cx2, cy2 = logic.hex_center(0, 1)
    expected_cx2 = 50 + (30 * 1.5 + 15)
    expected_cy2 = 50 + (30 * math.sqrt(3) + 15) / 2
    assert math.isclose(cx2, expected_cx2)
    assert math.isclose(cy2, expected_cy2)


def test_placement_and_border_lines():
    world = make_world()
    logic = StaticMapLogic(world, rows=3, cols=3, hex_size=30, spacing=15)
    logic.place_jarldomes_bfs(lambda _nid: 3)

    assert logic.map_static_positions[10] == (0, 0)
    assert logic.map_static_positions[20] == (1, 0)
    assert logic.map_static_positions[30] == (0, 1)

    lines = logic.border_lines()
    assert len(lines) == 1
    x1, y1, x2, y2, color, width = lines[0]
    assert color == "peru"
    assert width == 2

    cx10, cy10 = logic.hex_center(*logic.map_static_positions[10])
    cx20, cy20 = logic.hex_center(*logic.map_static_positions[20])
    assert math.isclose(x1, cx10)
    assert math.isclose(y1, cy10)
    assert math.isclose(x2, cx20)
    assert math.isclose(y2, cy20)
