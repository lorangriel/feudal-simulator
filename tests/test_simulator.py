import pytest
import tkinter as tk

from src import feodal_simulator as fs
from src.constants import DAY_LABORER_WORK_DAYS


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
        self.world_ui = fs.WorldManagerUI(save_func=lambda *a, **k: None)
        self.status_service = fs.StatusService()

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
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "name": "Furstendöme",
                "custom_name": "Uppland",
            },
            "3": {"node_id": 3, "parent_id": 2, "custom_name": "Gotland"},
            "4": {
                "node_id": 4,
                "parent_id": 3,
                "res_type": "Bageri",
                "custom_name": "",
                "ruler_id": 10,
            },
            "5": {"node_id": 5, "parent_id": 3},
        },
        "characters": {"10": {"name": "Duke"}},
        "next_node_id": 6,
    }
    sim = make_simulator(world)
    # depth 1 with custom name
    node = world["nodes"]["2"]
    assert (
        sim.get_display_name_for_node(node, 1)
        == "Furstendöme [Uppland] (ID: 2) (Kungarike)"
    )
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
            "1": {
                "node_id": 1,
                "parent_id": None,
                "name": "Kungarike",
                "children": [],
                "num_subfiefs": 0,
            }
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
            "10": {
                "node_id": 10,
                "parent_id": 1,
                "neighbors": [
                    {"id": None, "border": fs.NEIGHBOR_NONE_STR}
                    for _ in range(fs.MAX_NEIGHBORS)
                ],
                "custom_name": "A",
            },
            "20": {
                "node_id": 20,
                "parent_id": 1,
                "neighbors": [
                    {"id": None, "border": fs.NEIGHBOR_NONE_STR}
                    for _ in range(fs.MAX_NEIGHBORS)
                ],
                "custom_name": "B",
            },
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
    princ = sum(
        1 for n in world["nodes"].values() if wm.get_depth_of_node(n["node_id"]) == 1
    )
    duchies = sum(
        1 for n in world["nodes"].values() if wm.get_depth_of_node(n["node_id"]) == 2
    )
    jarls = sum(
        1 for n in world["nodes"].values() if wm.get_depth_of_node(n["node_id"]) == 3
    )
    assert princ == 4
    assert duchies == 15
    assert jarls >= 200


def test_save_current_world_refreshes_dynamic_map(monkeypatch):
    world = {"nodes": {}, "characters": {}}
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.active_world_name = "A"
    sim.world_data = world
    sim.all_worlds = {"A": world}
    sim.world_ui = fs.WorldManagerUI(save_func=lambda *a, **k: None)
    sim.status_service = fs.StatusService()
    sim.dynamic_map_view = type(
        "DM",
        (),
        {
            "set_world_data": lambda self, wd: setattr(self, "wd", wd),
            "draw_dynamic_map": lambda self: setattr(self, "redrawn", True),
        },
    )()
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


def test_load_world_uses_saved_positions():
    world = {
        "nodes": {
            "10": {"node_id": 10, "hex_row": 2, "hex_col": 3},
            "20": {"node_id": 20, "hex_row": 5, "hex_col": 1},
        },
        "characters": {},
    }
    sim = LoadStubSimulator()
    sim.world_manager = fs.WorldManager({})
    sim.static_rows = 35
    sim.static_cols = 35
    sim.all_worlds = {"A": world}
    fs.FeodalSimulator.load_world(sim, "A")
    assert sim.map_static_positions[10] == (2, 3)
    assert sim.map_static_positions[20] == (5, 1)


def test_load_world_updates_population_totals():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [3], "res_type": "Gods"},
            "3": {
                "node_id": 3,
                "parent_id": 2,
                "children": [],
                "res_type": "Bosättning",
                "free_peasants": 4,
            },
        },
        "characters": {},
    }
    sim = LoadStubSimulator()
    sim.world_manager = fs.WorldManager({})
    sim.static_rows = 1
    sim.static_cols = 1
    sim.all_worlds = {"A": world}

    fs.FeodalSimulator.load_world(sim, "A")

    assert sim.world_data["nodes"]["1"]["population"] == 4
    assert sim.world_data["nodes"]["2"]["population"] == 4
    assert sim.world_data["nodes"]["3"]["population"] == 4


def test_auto_link_adjacent_hexes_adds_neighbors():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "10": {"node_id": 10, "parent_id": 1},
            "101": {"node_id": 101, "parent_id": 10, "neighbors": []},
            "102": {"node_id": 102, "parent_id": 10, "neighbors": []},
        },
        "characters": {},
    }
    sim = make_simulator(world)
    sim.static_rows = 5
    sim.static_cols = 5
    sim.hex_spacing = 15
    sim.map_logic = fs.StaticMapLogic(world, rows=5, cols=5, hex_size=30, spacing=15)
    sim.get_depth_of_node = lambda nid: 3 if nid in (101, 102) else 0
    sim.world_manager.get_depth_of_node = sim.get_depth_of_node
    fs.FeodalSimulator.place_jarldomes_hierarchy(sim)
    fs.FeodalSimulator.auto_link_adjacent_hexes(sim)

    n101 = world["nodes"]["101"]["neighbors"][3]
    n102 = world["nodes"]["102"]["neighbors"][0]
    assert n101["id"] == 102 and n101["border"] == "liten väg"
    assert n102["id"] == 101 and n102["border"] == "liten väg"


def test_move_node_to_hex_relinks_neighbors():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "10": {"node_id": 10, "parent_id": 1, "neighbors": []},
            "20": {"node_id": 20, "parent_id": 1, "neighbors": []},
        },
        "characters": {},
    }
    sim = make_simulator(world)
    sim.static_rows = 4
    sim.static_cols = 4
    sim.hex_spacing = 15
    sim.map_logic = fs.StaticMapLogic(world, rows=4, cols=4, hex_size=30, spacing=15)
    sim.get_depth_of_node = lambda nid: 3 if nid in (10, 20) else 0
    sim.world_manager.get_depth_of_node = sim.get_depth_of_node
    sim.map_static_positions = {10: (0, 0), 20: (1, 0)}
    sim.static_grid_occupied = [[None] * 4 for _ in range(4)]
    sim.static_grid_occupied[0][0] = 10
    sim.static_grid_occupied[1][0] = 20
    sim.map_logic.map_static_positions = dict(sim.map_static_positions)
    sim.map_logic.static_grid_occupied = [row[:] for row in sim.static_grid_occupied]

    fs.FeodalSimulator.auto_link_adjacent_hexes(sim)
    assert any(nb.get("id") == 20 for nb in world["nodes"]["10"]["neighbors"])

    sim.move_node_to_hex(20, 3, 3)

    assert sim.map_static_positions[20] == (3, 3)
    assert sim.static_grid_occupied[1][0] is None
    assert all(nb.get("id") is None for nb in world["nodes"]["10"]["neighbors"])
    assert all(nb.get("id") is None for nb in world["nodes"]["20"]["neighbors"])


def test_move_node_only_clears_moved_neighbors():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "10": {"node_id": 10, "parent_id": 1, "neighbors": []},
            "20": {"node_id": 20, "parent_id": 1, "neighbors": []},
            "30": {"node_id": 30, "parent_id": 1, "neighbors": []},
        },
        "characters": {},
    }

    sim = make_simulator(world)
    sim.static_rows = 5
    sim.static_cols = 5
    sim.hex_spacing = 15
    sim.map_logic = fs.StaticMapLogic(world, rows=5, cols=5, hex_size=30, spacing=15)
    sim.get_depth_of_node = lambda nid: 3 if nid in (10, 20, 30) else 0
    sim.world_manager.get_depth_of_node = sim.get_depth_of_node
    sim.map_static_positions = {10: (0, 0), 20: (1, 0), 30: (0, 1)}
    sim.static_grid_occupied = [[None] * 5 for _ in range(5)]
    sim.static_grid_occupied[0][0] = 10
    sim.static_grid_occupied[1][0] = 20
    sim.static_grid_occupied[0][1] = 30
    sim.map_logic.map_static_positions = dict(sim.map_static_positions)
    sim.map_logic.static_grid_occupied = [row[:] for row in sim.static_grid_occupied]

    fs.FeodalSimulator.auto_link_adjacent_hexes(sim)
    assert any(nb.get("id") == 20 for nb in world["nodes"]["10"]["neighbors"])
    assert any(nb.get("id") == 30 for nb in world["nodes"]["10"]["neighbors"])

    sim.move_node_to_hex(20, 3, 3)

    assert all(nb.get("id") is None for nb in world["nodes"]["20"]["neighbors"])
    assert any(nb.get("id") == 30 for nb in world["nodes"]["10"]["neighbors"])
    assert all(nb.get("id") != 20 for nb in world["nodes"]["10"]["neighbors"])
    assert any(nb.get("id") == 10 for nb in world["nodes"]["30"]["neighbors"])


def test_move_node_removes_unidirectional_links():
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "10": {"node_id": 10, "parent_id": 1, "neighbors": []},
            "20": {"node_id": 20, "parent_id": 1, "neighbors": []},
            "30": {
                "node_id": 30,
                "parent_id": 1,
                "neighbors": [
                    {"id": 10, "border": "väg"},
                    {"id": 20, "border": "väg"},
                ]
                + [
                    {"id": None, "border": fs.NEIGHBOR_NONE_STR}
                    for _ in range(fs.MAX_NEIGHBORS - 2)
                ],
            },
        },
        "characters": {},
    }

    sim = make_simulator(world)
    sim.static_rows = 5
    sim.static_cols = 5
    sim.hex_spacing = 15
    sim.map_logic = fs.StaticMapLogic(world, rows=5, cols=5, hex_size=30, spacing=15)
    sim.get_depth_of_node = lambda nid: 3 if nid in (10, 20, 30) else 0
    sim.world_manager.get_depth_of_node = sim.get_depth_of_node
    sim.map_static_positions = {10: (0, 0), 20: (1, 0), 30: (0, 1)}
    sim.static_grid_occupied = [[None] * 5 for _ in range(5)]
    sim.static_grid_occupied[0][0] = 10
    sim.static_grid_occupied[1][0] = 20
    sim.static_grid_occupied[0][1] = 30
    sim.map_logic.map_static_positions = dict(sim.map_static_positions)
    sim.map_logic.static_grid_occupied = [row[:] for row in sim.static_grid_occupied]

    sim.move_node_to_hex(20, 3, 3)

    assert all(nb.get("id") is None for nb in world["nodes"]["20"]["neighbors"])
    assert all(nb.get("id") != 20 for nb in world["nodes"]["30"]["neighbors"])
    assert any(nb.get("id") == 10 for nb in world["nodes"]["30"]["neighbors"])


def test_clear_all_neighbor_links(monkeypatch):
    world = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "10": {
                "node_id": 10,
                "parent_id": 1,
                "neighbors": [{"id": 20, "border": "v\u00e4g"}]
                + [
                    {"id": None, "border": fs.NEIGHBOR_NONE_STR}
                    for _ in range(fs.MAX_NEIGHBORS - 1)
                ],
            },
            "20": {
                "node_id": 20,
                "parent_id": 1,
                "neighbors": [{"id": 10, "border": "v\u00e4g"}]
                + [
                    {"id": None, "border": fs.NEIGHBOR_NONE_STR}
                    for _ in range(fs.MAX_NEIGHBORS - 1)
                ],
            },
        },
        "characters": {},
    }

    sim = make_simulator(world)
    sim.root = object()
    sim.static_map_canvas = None
    sim.get_depth_of_node = lambda nid: 3 if nid in (10, 20) else 0
    sim.world_manager.get_depth_of_node = sim.get_depth_of_node
    calls = []
    sim.save_current_world = lambda: calls.append("saved")
    sim.draw_static_border_lines = lambda: calls.append("drawn")
    monkeypatch.setattr(fs.messagebox, "askyesno", lambda *a, **k: True)

    fs.FeodalSimulator.clear_all_neighbor_links(sim)

    assert all(nb.get("id") is None for nb in world["nodes"]["10"]["neighbors"])
    assert all(nb.get("id") is None for nb in world["nodes"]["20"]["neighbors"])
    assert "saved" in calls


def test_day_laborer_entry_color_and_work_update():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [],
                "dagsverken": "normalt",
                "day_laborers_available": 5,
                "day_laborers_hired": 0,
            }
        },
        "characters": {},
    }

    sim = DummySimulator()
    sim.world_data = world
    sim.world_manager = fs.WorldManager(world)
    sim.get_depth_of_node = lambda nid: 3
    sim._auto_save_field = lambda node, key, val, _r=False: node.__setitem__(key, val)
    sim._update_umbarande_totals = lambda *a, **k: None
    sim.show_neighbor_editor = lambda *a, **k: None
    sim.save_current_world = lambda: None
    sim.refresh_tree_item = lambda *a, **k: None

    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("Tk display not available")
    frame = tk.Frame(root)
    frame.pack()
    sim._show_jarldome_editor(frame, world["nodes"]["1"])

    sim.day_laborers_hired_var.set("3")
    root.update_idletasks()
    assert sim.day_laborers_hired_entry.cget("foreground") == "black"
    assert world["nodes"]["1"]["work_available"] == 3 * DAY_LABORER_WORK_DAYS

    sim.day_laborers_hired_var.set("6")
    root.update_idletasks()
    assert sim.day_laborers_hired_entry.cget("foreground") == "red"

    root.destroy()


def test_work_need_entry_color_updates():
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": None,
                "children": [],
                "dagsverken": "normalt",
                "day_laborers_available": 5,
                "day_laborers_hired": 0,
                "work_needed": 0,
            }
        },
        "characters": {},
    }

    sim = DummySimulator()
    sim.world_data = world
    sim.world_manager = fs.WorldManager(world)
    sim.get_depth_of_node = lambda nid: 3
    sim._auto_save_field = lambda node, key, val, _r=False: node.__setitem__(key, val)
    sim._update_umbarande_totals = lambda *a, **k: None
    sim.show_neighbor_editor = lambda *a, **k: None
    sim.save_current_world = lambda: None
    sim.refresh_tree_item = lambda *a, **k: None

    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("Tk display not available")
    frame = tk.Frame(root)
    frame.pack()
    sim._show_jarldome_editor(frame, world["nodes"]["1"])

    sim.work_need_var.set(str(DAY_LABORER_WORK_DAYS + 30))
    root.update_idletasks()
    assert sim.work_need_entry.cget("foreground") == "red"

    sim.day_laborers_hired_var.set("2")
    root.update_idletasks()
    assert sim.work_need_entry.cget("foreground") == "black"

    root.destroy()
