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
    sim.world_manager = fs.WorldManager(world_data)
    # stub methods used in unit tests
    sim.store_tree_state = lambda: (set(), ())
    sim.populate_tree = lambda: None
    sim.restore_tree_state = lambda *args, **kwargs: None
    sim.show_node_view = lambda *args, **kwargs: None
    sim.save_current_world = lambda: None
    sim.add_status_message = lambda *args, **kwargs: None
    sim.draw_static_border_lines = lambda: None
    return sim


class LoadStubSimulator(DummySimulator):
    def __init__(self):
        super().__init__()
        self.all_worlds = {}
        self.root = type("R", (), {"title": lambda self, *_args: None})()
        self.tree = type("T", (), {"winfo_exists": lambda self: False})()
        self.show_no_world_view = lambda *a, **k: None
        self._auto_select_single_root = lambda *a, **k: None
        self.hide_map_mode_buttons = lambda *a, **k: None
        self.add_status_message = lambda *a, **k: None

    def load_world(self, wname):
        self.active_world_name = wname
        self.world_data = self.all_worlds[wname]
        self.world_manager = fs.WorldManager(self.world_data)


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
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "name": "Kungarike"},
            "2": {"node_id": 2, "parent_id": 1, "name": "Furstendöme", "custom_name": "Uppland"},
            "3": {"node_id": 3, "parent_id": 2, "custom_name": "Gotland"},
            "4": {"node_id": 4, "parent_id": 3, "res_type": "Bageri", "custom_name": "", "ruler_id": 10},
            "5": {"node_id": 5, "parent_id": 3},
        },
        "characters": {"10": {"name": "Duke"}},
        "next_node_id": 6,
    }
    sim = make_simulator(world)
    # depth 1 with custom name
    node = world["nodes"]["2"]
    assert sim.get_display_name_for_node(node, 1) == "Furstendöme [Uppland] (ID: 2) (Kungarike)"
    # depth 3 jarldom
    node_j = world["nodes"]["3"]
    assert sim.get_display_name_for_node(node_j, 3) == "Gotland (Uppland)"
    # depth 4 resource with ruler
    node_r = world["nodes"]["4"]
    assert sim.get_display_name_for_node(node_r, 4) == "Bageri - (Duke) (Gotland)"
    # depth 4 with minimal data
    node_r2 = world["nodes"]["5"]
    assert sim.get_display_name_for_node(node_r2, 4) == "Resurs 5 (Gotland)"


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
    sim.world_manager.get_depth_of_node = lambda nid: 3
    messages = []
    sim.add_status_message = lambda msg: messages.append(msg)
    sim.attempt_link_neighbors(10, 20)
    assert world["nodes"]["10"]["neighbors"][0]["id"] == 20
    assert world["nodes"]["20"]["neighbors"][0]["id"] == 10
    assert any("nu grannar" in m for m in messages)


def test_create_drunok_world_builds_structure(monkeypatch):
    sim = LoadStubSimulator()
    monkeypatch.setattr(fs.messagebox, "askyesno", lambda *a, **k: True)
    sim.create_drunok_world()
    assert "Drunok" in sim.all_worlds
    world = sim.all_worlds["Drunok"]
    root = world["nodes"]["1"]
    assert root["custom_name"] == "Drunok"
    wm = fs.WorldManager(world)
    princ = sum(1 for n in world["nodes"].values() if wm.get_depth_of_node(n["node_id"]) == 1)
    duchies = sum(1 for n in world["nodes"].values() if wm.get_depth_of_node(n["node_id"]) == 2)
    jarls = sum(1 for n in world["nodes"].values() if wm.get_depth_of_node(n["node_id"]) == 3)
    assert princ == 4
    assert duchies == 15
    assert jarls >= 200


def test_save_current_world_refreshes_dynamic_map(monkeypatch):
    world = {"nodes": {}, "characters": {}}
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.active_world_name = "A"
    sim.world_data = world
    sim.all_worlds = {"A": world}
    sim.dynamic_map_view = type(
        "DM",
        (),
        {
            "set_world_data": lambda self, wd: setattr(self, "wd", wd),
            "draw_dynamic_map": lambda self: setattr(self, "redrawn", True),
        },
    )()
    monkeypatch.setattr(fs, "save_worlds_to_file", lambda data: None)
    sim.refresh_dynamic_map = fs.FeodalSimulator.refresh_dynamic_map.__get__(sim)
    fs.FeodalSimulator.save_current_world(sim)
    assert sim.dynamic_map_view.wd is world
    assert getattr(sim.dynamic_map_view, "redrawn", False)


def test_save_static_positions_updates_nodes():
    world = {
        "nodes": {
            "10": {"node_id": 10},
            "20": {"node_id": 20},
        },
        "characters": {},
        "next_node_id": 21,
    }
    sim = make_simulator(world)
    sim.map_static_positions = {10: (1, 2), 20: (3, 4)}
    saved = []
    sim.save_current_world = lambda: saved.append(True)
    sim.save_static_positions()
    assert world["nodes"]["10"]["hex_row"] == 1
    assert world["nodes"]["10"]["hex_col"] == 2
    assert world["nodes"]["20"]["hex_row"] == 3
    assert world["nodes"]["20"]["hex_col"] == 4
    assert saved
