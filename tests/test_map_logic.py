import math
from src.map_logic import StaticMapLogic
from src.constants import NEIGHBOR_NONE_STR, MAX_NEIGHBORS


def make_world():
    empty = [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]
    n10 = empty.copy()
    n20 = empty.copy()
    n10[3] = {"id": 20, "border": "v\u00e4g"}
    n20[0] = {"id": 10, "border": "v\u00e4g"}
    return {
        "nodes": {
            "10": {"node_id": 10, "neighbors": n10},
            "20": {"node_id": 20, "neighbors": n20},
            "30": {"node_id": 30, "neighbors": empty.copy()},
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

    start = logic.hex_side_center(*logic.map_static_positions[10], 4)
    end = logic.hex_side_center(*logic.map_static_positions[20], 1)
    assert math.isclose(x1, start[0])
    assert math.isclose(y1, start[1])
    assert math.isclose(x2, end[0])
    assert math.isclose(y2, end[1])


def make_world_west():
    empty = [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]
    n10 = empty.copy()
    n20 = empty.copy()
    n10[5] = {"id": 20, "border": NEIGHBOR_NONE_STR}
    n20[2] = {"id": 10, "border": NEIGHBOR_NONE_STR}
    return {
        "nodes": {
            "10": {"node_id": 10, "neighbors": n10},
            "20": {"node_id": 20, "neighbors": n20},
        },
        "characters": {},
    }


def test_component_shift_for_western_neighbor():
    world = make_world_west()
    logic = StaticMapLogic(world, rows=4, cols=4, hex_size=30, spacing=15)
    logic.place_jarldomes_bfs(lambda _nid: 3)

    pos10 = logic.map_static_positions[10]
    pos20 = logic.map_static_positions[20]
    assert logic.direction_index(*pos10, *pos20) == 6
