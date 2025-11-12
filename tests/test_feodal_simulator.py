import random
import types
import tkinter as tk
from tkinter import ttk

import pytest

from src import feodal_simulator as fs


def test_commit_pending_changes_calls_callback_and_clears():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    called = []

    def cb():
        called.append(True)

    sim.pending_save_callback = cb
    fs.FeodalSimulator.commit_pending_changes(sim)
    assert called and sim.pending_save_callback is None


def test_entry_char_id_helper():
    assert fs.FeodalSimulator._entry_char_id({"kind": "character", "char_id": "7"}) == 7
    assert fs.FeodalSimulator._entry_char_id({"kind": "character", "char_id": 3}) == 3
    assert fs.FeodalSimulator._entry_char_id({"kind": "placeholder", "label": ""}) is None
    assert fs.FeodalSimulator._entry_char_id(None) is None


def test_make_return_to_node_command_uses_latest():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    latest_node = {"node_id": 5, "value": "new"}
    sim.world_data = {"nodes": {"5": latest_node}}
    called = []

    def fake_show(self, node):
        called.append(node)

    sim.show_node_view = types.MethodType(fake_show, sim)
    original = {"node_id": 5, "value": "old"}
    command = fs.FeodalSimulator._make_return_to_node_command(sim, original)
    command()
    assert called == [latest_node]


def test_make_return_to_node_command_falls_back():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {"nodes": {}}
    called = []

    def fake_show(self, node):
        called.append(node)

    sim.show_node_view = types.MethodType(fake_show, sim)
    original = {"node_id": 9, "value": "orig"}
    command = fs.FeodalSimulator._make_return_to_node_command(sim, original)
    command()
    assert called == [original]


def test_open_character_editor_calls_editor(monkeypatch):
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    char_data = {"char_id": 1, "name": "Test"}
    sim.world_data = {"characters": {"1": char_data}}
    sim.root = None
    captured = {}

    def fake_show(
        self,
        char,
        *,
        is_new=False,
        parent_node_data=None,
        after_save=None,
        return_command=None,
    ):
        captured["char"] = char
        captured["is_new"] = is_new
        captured["return_command"] = return_command

    sim.show_edit_character_view = types.MethodType(fake_show, sim)
    errors = []
    monkeypatch.setattr(fs.messagebox, "showerror", lambda *args, **kwargs: errors.append(args))
    returns = []
    return_command = lambda: returns.append(True)
    sim._open_character_editor(1, return_command)
    assert captured["char"] is char_data
    assert captured["is_new"] is False
    assert captured["return_command"] is return_command
    captured["return_command"]()
    assert returns == [True]
    assert errors == []


def test_open_character_editor_missing_shows_error(monkeypatch):
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {"characters": {}}
    sim.root = None
    sim.show_edit_character_view = types.MethodType(lambda *args, **kwargs: None, sim)
    errors = []
    monkeypatch.setattr(fs.messagebox, "showerror", lambda *args, **kwargs: errors.append(args))
    sim._open_character_editor(42, lambda: None)
    assert errors


def _make_sim_with_world(characters):
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {"characters": characters}
    return sim


def test_get_sorted_character_choices_orders_casefolded():
    sim = _make_sim_with_world(
        {
            "2": {"name": "Bertil"},
            "1": {"name": "Åke"},
            "3": {"name": "adam"},
        }
    )

    assert sim._get_sorted_character_choices() == [
        (3, "adam"),
        (2, "Bertil"),
        (1, "Åke"),
    ]


def test_find_generic_character_id_returns_smallest():
    sim = _make_sim_with_world(
        {
            "10": {"name": "Generisk"},
            "7": {"name": " generisk "},
            "3": {"name": "Annan"},
            "foo": {"name": "Generisk"},
        }
    )

    assert sim._find_generic_character_id() == 7


def test_coerce_person_entry_handles_various_inputs():
    sim = _make_sim_with_world({})
    default_label = "saknas"

    assert sim._coerce_person_entry({"kind": "character", "char_id": "5"}, default_label) == {
        "kind": "character",
        "char_id": 5,
    }
    assert sim._coerce_person_entry({"char_id": 6}, default_label) == {
        "kind": "character",
        "char_id": 6,
    }
    assert sim._coerce_person_entry({"kind": "placeholder", "label": ""}, default_label) == {
        "kind": "placeholder",
        "label": default_label,
    }
    assert sim._coerce_person_entry("15", default_label) == {
        "kind": "character",
        "char_id": 15,
    }
    assert sim._coerce_person_entry("", default_label) == {
        "kind": "placeholder",
        "label": default_label,
    }
    assert sim._coerce_person_entry(3.0, default_label) == {
        "kind": "character",
        "char_id": 3,
    }
    assert sim._coerce_person_entry(object(), default_label) is None


def test_normalise_person_entries_wraps_single_and_filters():
    sim = _make_sim_with_world({})
    default_label = "saknas"

    raw = [
        {"kind": "character", "char_id": "2"},
        "placeholder",
        None,
    ]
    assert sim._normalise_person_entries(raw, default_label) == [
        {"kind": "character", "char_id": 2},
        {"kind": "placeholder", "label": "placeholder"},
    ]

    # Single entry becomes list
    assert sim._normalise_person_entries({"char_id": 9}, default_label) == [
        {"kind": "character", "char_id": 9},
    ]


def test_person_entry_display_uses_character_name_and_fallbacks(monkeypatch):
    sim = _make_sim_with_world({})
    characters = {"1": {"name": "Anna"}}

    assert sim._person_entry_display({"kind": "character", "char_id": 1}, characters) == "1: Anna"

    # Missing character falls back to ID string
    assert sim._person_entry_display({"kind": "character", "char_id": 4}, characters) == "4: ID 4"

    # Placeholder just returns label
    assert (
        sim._person_entry_display(
            {"kind": "placeholder", "label": "Okänd"}, characters
        )
        == "Okänd"
    )


def test_grid_set_visibility_handles_missing_widgets():
    class DummyMaster:
        def __init__(self, *, exists=True, fail=False):
            self.exists = exists
            self.fail = fail

        def winfo_exists(self):
            if self.fail:
                raise tk.TclError("master missing")
            return int(self.exists)

    class DummyWidget:
        def __init__(
            self,
            *,
            exists=True,
            fail_exists=False,
            master=None,
            manager="grid",
            fail_manager=False,
            grid_fail=False,
            grid_remove_fail=False,
        ):
            self.exists = exists
            self.fail_exists = fail_exists
            self.master = master
            self.manager = manager
            self.fail_manager = fail_manager
            self.grid_fail = grid_fail
            self.grid_remove_fail = grid_remove_fail
            self.grid_calls = 0
            self.grid_remove_calls = 0

        def winfo_exists(self):
            if self.fail_exists:
                raise tk.TclError("bad widget")
            return int(self.exists)

        def winfo_manager(self):
            if self.fail_manager:
                raise tk.TclError("manager broken")
            return self.manager

        def grid(self):
            if self.grid_fail or not self.exists:
                raise tk.TclError("missing")
            self.grid_calls += 1

        def grid_remove(self):
            if self.grid_remove_fail or not self.exists:
                raise tk.TclError("missing")
            self.grid_remove_calls += 1

    existing = DummyWidget()
    missing = DummyWidget(exists=False)
    broken = DummyWidget(fail_exists=True)
    master_missing = DummyMaster(exists=False)
    orphaned = DummyWidget(master=master_missing)
    wrong_manager = DummyWidget(manager="pack")
    grid_failure = DummyWidget(grid_fail=True)

    fs.FeodalSimulator._grid_set_visibility(
        [existing, missing, broken, orphaned, wrong_manager, grid_failure], True
    )
    assert existing.grid_calls == 1
    assert missing.grid_calls == 0
    assert broken.grid_calls == 0
    assert orphaned.grid_calls == 0
    assert wrong_manager.grid_calls == 0
    assert grid_failure.grid_calls == 0

    failing_remove = DummyWidget(grid_remove_fail=True)

    fs.FeodalSimulator._grid_set_visibility(
        [existing, missing, broken, failing_remove], False
    )
    assert existing.grid_remove_calls == 1
    assert missing.grid_remove_calls == 0
    assert broken.grid_remove_calls == 0
    assert failing_remove.grid_remove_calls == 0


def test_noble_family_editor_uses_tabs_for_spouses_and_relatives():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        editor_frame = ttk.Frame(root)
        editor_frame.grid()

        sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
        sim.world_data = {
            "characters": {
                "1": {"name": "Herre"},
                "2": {"name": "Partner"},
            },
            "nodes": {},
        }
        sim.save_current_world = lambda: None
        sim._open_character_editor = lambda *args, **kwargs: None
        sim._open_character_creator_for_node = lambda *args, **kwargs: None
        sim._create_delete_button = lambda parent, *_args, **_kwargs: ttk.Button(
            parent, text="Radera"
        )
        sim.show_no_world_view = lambda: None
        sim.show_node_view = lambda node: None

        node_data = {
            "node_id": 1,
            "noble_standard": "Välbärgad",
            "noble_lord": {"kind": "character", "char_id": 1},
            "noble_spouses": [{"kind": "character", "char_id": 2}],
            "noble_children": [],
            "noble_relatives": [],
        }

        sim._show_noble_family_editor(editor_frame, node_data, depth=0, start_row=0)

        notebooks = [
            child for child in editor_frame.winfo_children() if isinstance(child, ttk.Notebook)
        ]
        assert len(notebooks) == 1
        notebook = notebooks[0]
        tab_ids = notebook.tabs()
        tab_texts = [notebook.tab(tab_id, "text") for tab_id in tab_ids]
        assert tab_texts == ["Gemål", "Släktingar", "Tjänstefolk"]

        def collect_texts(widget):
            texts = []
            try:
                value = widget.cget("text")
            except tk.TclError:
                value = None
            if value:
                texts.append(value)
            for child in widget.winfo_children():
                texts.extend(collect_texts(child))
            return texts

        spouse_tab_widget = notebook.nametowidget(tab_ids[0])
        relatives_tab_widget = notebook.nametowidget(tab_ids[1])
        staff_tab_widget = notebook.nametowidget(tab_ids[2])

        spouse_texts = collect_texts(spouse_tab_widget)
        assert "Gemål:" in spouse_texts
        assert "Barn:" in spouse_texts

        relatives_texts = collect_texts(relatives_tab_widget)
        assert "Släktingar:" in relatives_texts
        assert "Barn:" not in relatives_texts

        staff_texts = collect_texts(staff_tab_widget)
        assert "Antal adliga (A):" in staff_texts
        assert "Levnadsnivå:" in staff_texts
        assert "Total kostnad per år:" in staff_texts
    finally:
        root.destroy()


def test_noble_family_editor_places_lord_before_standard():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        editor_frame = ttk.Frame(root)
        editor_frame.grid()

        sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
        sim.world_data = {
            "characters": {
                "1": {"name": "Herre"},
                "2": {"name": "Partner"},
            },
            "nodes": {},
        }
        sim.save_current_world = lambda: None
        sim._open_character_editor = lambda *args, **kwargs: None
        sim._open_character_creator_for_node = lambda *args, **kwargs: None
        sim._create_delete_button = lambda parent, *_args, **_kwargs: ttk.Button(
            parent, text="Radera"
        )
        sim.show_no_world_view = lambda: None
        sim.show_node_view = lambda node: None

        node_data = {
            "node_id": 1,
            "noble_standard": "Välbärgad",
            "noble_lord": {"kind": "character", "char_id": 1},
            "noble_spouses": [{"kind": "character", "char_id": 2}],
            "noble_children": [],
            "noble_relatives": [],
        }

        sim._show_noble_family_editor(editor_frame, node_data, depth=0, start_row=0)

        label_rows = {
            child.cget("text"): int(child.grid_info()["row"])
            for child in editor_frame.grid_slaves()
            if isinstance(child, ttk.Label)
        }

        assert label_rows["Länsherre:"] == 0
        assert label_rows["Levnadsstandard:"] == 1
        assert label_rows["Bostadskrav:"] == 1

        combobox_positions = {
            (int(child.grid_info()["row"]), int(child.grid_info()["column"]))
            for child in editor_frame.grid_slaves()
            if isinstance(child, ttk.Combobox)
        }

        assert (0, 1) in combobox_positions
        assert (1, 1) in combobox_positions

        edit_button_positions = {
            (int(child.grid_info()["row"]), int(child.grid_info()["column"]))
            for child in editor_frame.grid_slaves()
            if isinstance(child, ttk.Button) and child.cget("text") == "Editera"
        }

        assert (0, 3) in edit_button_positions
    finally:
        root.destroy()


def test_generate_auto_character_name_inherits_surname():
    state = random.getstate()
    try:
        random.seed(0)
        name = fs.FeodalSimulator._generate_auto_character_name("m", "Tor")
    finally:
        random.setstate(state)

    parts = name.split()
    assert parts[-1] == "Tor"
    assert len(parts) >= 2


def test_make_relation_creation_context_includes_surname():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {"characters": {"7": {"name": "Garan Tel"}}}

    sim.get_depth_of_node = types.MethodType(lambda self, node_id: 3, sim)
    sim.get_display_name_for_node = types.MethodType(
        lambda self, node_data, depth: node_data.get("name", f"Node {node_data.get('node_id')}")
        if isinstance(node_data, dict)
        else "",
        sim,
    )

    node_data = {
        "node_id": 5,
        "name": "Jarldöme Test",
        "noble_lord": {"kind": "character", "char_id": 7},
    }

    context = sim._make_relation_creation_context(node_data, "child")

    assert context["inherit_surname"] is True
    assert context["inherited_surname"] == "Tel"
    assert context["node_name"] == "Jarldöme Test"
    assert context["lord_name"] == "Garan Tel"


def test_gather_liege_relationships_identifies_roles():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {
        "characters": {
            "1": {"name": "Lord One"},
            "2": {"name": "Spouse"},
            "3": {"name": "Child"},
            "4": {"name": "Relative"},
        },
        "nodes": {
            "10": {
                "node_id": 10,
                "name": "Jarldöme Ten",
                "noble_lord": {"kind": "character", "char_id": 1},
                "noble_spouses": [{"kind": "character", "char_id": 2}],
                "noble_spouse_children": [
                    [{"kind": "character", "char_id": 3}]
                ],
                "noble_relatives": [{"kind": "character", "char_id": 4}],
            }
        },
    }

    sim.get_depth_of_node = types.MethodType(lambda self, node_id: 3, sim)
    sim.get_display_name_for_node = types.MethodType(
        lambda self, node_data, depth: node_data.get("name", f"Node {node_data.get('node_id')}")
        if isinstance(node_data, dict)
        else "",
        sim,
    )

    spouse_rel = sim._gather_liege_relationships(2)
    assert {rel["kind"] for rel in spouse_rel} == {"spouse"}
    assert spouse_rel[0]["lord_name"] == "Lord One"

    child_rel = sim._gather_liege_relationships(3)
    assert {rel["kind"] for rel in child_rel} == {"child"}
    assert child_rel[0]["node_name"] == "Jarldöme Ten"

    relative_rel = sim._gather_liege_relationships(4)
    assert {rel["kind"] for rel in relative_rel} == {"relative"}
