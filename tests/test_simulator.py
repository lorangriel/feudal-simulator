import pytest

from src import feodal_simulator as fs


class DummySimulator(fs.FeodalSimulator):
    """Minimal subclass that avoids GUI setup."""
    def __init__(self):
        # bypass parent __init__
        pass

def make_simulator(world_data):
    sim = DummySimulator()
    sim.world_data = world_data
    sim._depth_cache = {}
    # stub methods used in unit tests
    sim.store_tree_state = lambda: (set(), ())
    sim.populate_tree = lambda: None
    sim.restore_tree_state = lambda *args, **kwargs: None
    sim.show_node_view = lambda *args, **kwargs: None
    sim.save_current_world = lambda: None
    sim.add_status_message = lambda *args, **kwargs: None
    sim.draw_static_border_lines = lambda: None
    return sim


def test_get_depth_of_node_and_cycles():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "2": {"node_id": 2, "parent_id": 1},
            "3": {"node_id": 3, "parent_id": 2},
            "4": {"node_id": 4, "parent_id": 9},  # missing parent
            "5": {"node_id": 5, "parent_id": 6},
            "6": {"node_id": 6, "parent_id": 5},  # cycle
        },
        "characters": {},
        "next_node_id": 6,
    }
    sim = make_simulator(world)
    assert sim.get_depth_of_node(1) == 0
    assert sim.get_depth_of_node(3) == 2
    assert sim.get_depth_of_node(4) == 0  # orphan treated as depth 0
    assert sim.get_depth_of_node(5) == -99  # cycle detected


def test_get_display_name_for_node():
    world = {
        "nodes": {},
        "characters": {"10": {"name": "Duke"}},
        "next_node_id": 2,
    }
    sim = make_simulator(world)
    # depth 1 with custom name
    node = {"node_id": 2, "parent_id": 1, "name": "Furstendöme", "custom_name": "Uppland"}
    assert sim.get_display_name_for_node(node, 1) == "Furstendöme [Uppland] (ID: 2)"
    # depth 3 jarldom
    node_j = {"node_id": 3, "custom_name": "Gotland"}
    assert sim.get_display_name_for_node(node_j, 3) == "Gotland"
    # depth 4 resource with ruler
    node_r = {"node_id": 4, "res_type": "Bageri", "custom_name": "", "ruler_id": 10}
    sim.world_data["characters"]["10"] = {"name": "Duke"}
    assert sim.get_display_name_for_node(node_r, 4) == "Bageri - (Duke)"
    # depth 4 with minimal data
    node_r2 = {"node_id": 5}
    assert sim.get_display_name_for_node(node_r2, 4) == "Resurs 5"


def test_update_subfiefs_for_node_add_and_remove():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "name": "Kungarike", "children": [], "num_subfiefs": 0}
        },
        "characters": {},
        "next_node_id": 1,
    }
    sim = make_simulator(world)
    root = world["nodes"]["1"]
    root["num_subfiefs"] = 2
    sim.update_subfiefs_for_node(root)
    assert len(root["children"]) == 2
    assert set(root["children"]) == {2, 3}
    assert world["nodes"]["2"]["parent_id"] == 1
    # now reduce to one child
    root["num_subfiefs"] = 1
    sim.update_subfiefs_for_node(root)
    assert len(root["children"]) == 1
    assert root["children"][0] in {2, 3}
    remaining_id = root["children"][0]
    removed_id = 3 if remaining_id == 2 else 2
    assert str(removed_id) not in world["nodes"]


def test_attempt_link_neighbors_success():
    world = {
        "nodes": {
            "10": {"node_id": 10, "parent_id": 1, "neighbors": [{"id": None, "border": fs.NEIGHBOR_NONE_STR} for _ in range(fs.MAX_NEIGHBORS)], "custom_name": "A"},
            "20": {"node_id": 20, "parent_id": 1, "neighbors": [{"id": None, "border": fs.NEIGHBOR_NONE_STR} for _ in range(fs.MAX_NEIGHBORS)], "custom_name": "B"},
        },
        "characters": {},
        "next_node_id": 20,
    }
    sim = make_simulator(world)
    # Provide depth cache function result: treat both as depth 3
    sim.get_depth_of_node = lambda nid: 3
    messages = []
    sim.add_status_message = lambda msg: messages.append(msg)
    sim.attempt_link_neighbors(10, 20)
    assert world["nodes"]["10"]["neighbors"][0]["id"] == 20
    assert world["nodes"]["20"]["neighbors"][0]["id"] == 10
    assert any("nu grannar" in m for m in messages)
