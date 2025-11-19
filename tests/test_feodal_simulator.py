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


class DummyWidget:
    def __init__(self, *, exists="1", master=None, manager="grid"):
        self._exists = exists
        self.master = master
        self._manager = manager
        self.grid_called = False
        self.grid_remove_called = False

    def winfo_exists(self):
        return self._exists

    def winfo_manager(self):
        return self._manager

    def grid(self):
        self.grid_called = True

    def grid_remove(self):
        self.grid_remove_called = True


def _make_sim_with_world_data(world=None):
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = world or {"nodes": {}, "characters": {}}
    sim.add_status_message = lambda *_args, **_kwargs: None
    sim.save_current_world = lambda: None
    sim.root = None
    return sim


def test_grid_set_visibility_skips_destroyed_widgets():
    widget = DummyWidget(exists="0")
    fs.FeodalSimulator._grid_set_visibility((widget,), True)
    assert widget.grid_called is False


def test_grid_set_visibility_checks_master_existence():
    master = DummyWidget(exists="0")
    widget = DummyWidget(master=master)
    fs.FeodalSimulator._grid_set_visibility((widget,), True)
    assert widget.grid_called is False


def test_grid_set_visibility_hides_widgets():
    widget = DummyWidget()
    fs.FeodalSimulator._grid_set_visibility((widget,), False)
    assert widget.grid_remove_called is True


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


def test_show_edit_character_view_uses_scrollable_frame():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()

    try:
        sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
        sim.root = root
        sim.right_frame = ttk.Frame(root)
        sim.right_frame.pack()
        sim.static_map_canvas = None
        sim.dynamic_map_view = None
        sim.world_data = {
            "characters": {
                "1": {"char_id": 1, "name": "Test", "gender": "Man"}
            },
            "nodes": {},
        }
        sim.world_manager = fs.WorldManager(sim.world_data)
        sim.pending_save_callback = None
        sim.add_status_message = lambda *a, **k: None
        sim.save_current_world = lambda: None
        sim.refresh_tree_item = lambda *a, **k: None
        sim.show_manage_characters_view = lambda: None
        sim.show_node_view = lambda *_: None
        sim._generate_auto_character_name = lambda *_: "Auto"
        sim.tree = types.SimpleNamespace(winfo_exists=lambda: False)

        sim.show_edit_character_view(sim.world_data["characters"]["1"], is_new=False)
        root.update_idletasks()

        children = sim.right_frame.winfo_children()
        assert len(children) == 1
        scrollable = children[0]
        assert scrollable.__class__.__name__ == "ScrollableFrame"
        assert scrollable.__class__.__module__.endswith("utils")
        canvas_children = [
            child for child in scrollable.winfo_children() if isinstance(child, tk.Canvas)
        ]
        assert canvas_children, "Scrollbehållaren ska använda en canvas"
        assert hasattr(scrollable, "vscroll")
        assert scrollable.vscroll.cget("orient") == "vertical"
        titles = [
            child.cget("text")
            for child in scrollable.content.winfo_children()
            if hasattr(child, "cget")
        ]
        assert any("Karakt" in text for text in titles)
    finally:
        root.destroy()


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


def test_widget_exists_handles_destroyed_widgets():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        frame = ttk.Frame(root)
        frame.pack()
        assert fs.FeodalSimulator._widget_exists(frame)
        frame.destroy()
        assert not fs.FeodalSimulator._widget_exists(frame)
        assert not fs.FeodalSimulator._widget_exists(None)
    finally:
        root.destroy()


def test_destroy_child_widgets_is_safe_on_destroyed_parent():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        frame = ttk.Frame(root)
        frame.pack()
        child = ttk.Frame(frame)
        child.pack()
        fs.FeodalSimulator._destroy_child_widgets(frame)
        assert not child.winfo_exists()
        frame.destroy()
        fs.FeodalSimulator._destroy_child_widgets(frame)
    finally:
        root.destroy()


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


def test_noble_family_children_display_once_with_character_names():
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
                "1": {"name": "Lord"},
                "2": {"name": "Partner"},
                "3": {"name": "Barn"},
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
            "noble_spouse_children": [[{"kind": "character", "char_id": 3}]],
            "noble_children": [{"kind": "character", "char_id": 3}],
            "noble_relatives": [],
        }

        sim._show_noble_family_editor(editor_frame, node_data, depth=0, start_row=0)

        notebook = next(
            child
            for child in editor_frame.winfo_children()
            if isinstance(child, ttk.Notebook)
        )
        spouse_tab = notebook.nametowidget(notebook.tabs()[0])

        def collect_widgets(widget, cls):
            collected = []
            if isinstance(widget, cls):
                collected.append(widget)
            for child in widget.winfo_children():
                collected.extend(collect_widgets(child, cls))
            return collected

        child_display = sim._format_character_display(3, "Barn")
        child_combos = [
            widget
            for widget in collect_widgets(spouse_tab, ttk.Combobox)
            if widget.get() == child_display
        ]

        assert len(child_combos) == 1
        assert child_combos[0].get() == child_display
    finally:
        root.destroy()


def test_creating_noble_lord_updates_combobox_immediately():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        editor_frame = ttk.Frame(root)
        editor_frame.grid()

        sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
        sim.root = root
        sim.world_data = {"characters": {}, "nodes": {}}
        sim.add_status_message = lambda *_args, **_kwargs: None
        sim.save_current_world = lambda: None
        sim._open_character_editor = lambda *args, **kwargs: None
        sim._create_delete_button = lambda parent, *_args, **_kwargs: ttk.Button(
            parent, text="Radera"
        )
        sim.show_no_world_view = lambda: None
        sim.show_node_view = lambda node: None
        sim._generate_auto_character_name = lambda _gender_code, _surname: "Auto Lord"

        node_data = {"node_id": 1, "noble_standard": "Välbärgad"}

        sim._show_noble_family_editor(editor_frame, node_data, depth=0, start_row=0)

        lord_combo = None
        for child in editor_frame.grid_slaves():
            if not isinstance(child, ttk.Combobox):
                continue
            info = child.grid_info()
            if int(info.get("row", -1)) == 0 and int(info.get("column", -1)) == 1:
                lord_combo = child
                break

        assert lord_combo is not None, "Expected to find combobox for länsherre"
        assert lord_combo.get() == ""

        lord_combo.set("Ny")
        lord_combo.event_generate("<<ComboboxSelected>>")
        root.update_idletasks()

        entry = node_data.get("noble_lord")
        assert isinstance(entry, dict)
        assert entry.get("kind") == "character"
        display_value = lord_combo.get()
        assert display_value
        values = lord_combo.cget("values")
        if isinstance(values, str):
            values = (values,)
        assert display_value in values
        char_id = entry.get("char_id")
        assert isinstance(char_id, int)
        assert str(char_id) in display_value
        assert str(char_id) in sim.world_data["characters"]
    finally:
        root.destroy()


def test_available_noble_standards_use_buildings():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "res_type": "Byggnader",
                "buildings": [{"type": "Trästuga 2 våningar", "count": 1}],
            },
        }
    }

    node_data = {"node_id": 3, "parent_id": 1}

    available = sim._available_noble_standards(node_data)

    assert available == {"Enkel", "Anständig"}


def test_available_noble_standards_empty_without_buildings():
    sim = _make_sim_with_world_data({"nodes": {"1": {"node_id": 1, "parent_id": None}}})
    node_data = {"node_id": 2, "parent_id": 1}

    assert sim._available_noble_standards(node_data) == set()


def _find_combobox_with_value(widget, target):
    if isinstance(widget, ttk.Combobox):
        values = widget.cget("values")
        if isinstance(values, str):
            values = widget.tk.splitlist(values)
        if target in values:
            return widget
    for child in widget.winfo_children():
        found = _find_combobox_with_value(child, target)
        if found is not None:
            return found
    return None


def _combobox_values(combo):
    values = combo.cget("values")
    if isinstance(values, str):
        return combo.tk.splitlist(values)
    return tuple(values)


def test_new_noble_family_defaults_to_enkel():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        editor_frame = ttk.Frame(root)
        editor_frame.grid()

        sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
        sim.root = root
        sim.world_data = {
            "characters": {},
            "nodes": {
                "1": {"node_id": 1, "parent_id": None},
                "2": {
                    "node_id": 2,
                    "parent_id": 1,
                    "res_type": "Byggnader",
                    "buildings": [{"type": "Stenhus", "count": 1}],
                },
            },
        }
        sim.add_status_message = lambda *_args, **_kwargs: None
        sim.save_current_world = lambda: None
        sim._open_character_editor = lambda *args, **kwargs: None
        sim._create_delete_button = lambda parent, *_args, **_kwargs: ttk.Button(
            parent, text="Radera"
        )
        sim.show_no_world_view = lambda: None
        sim.show_node_view = lambda node: None

        node_data = {"node_id": 3, "parent_id": 1}

        sim._show_noble_family_editor(editor_frame, node_data, depth=0, start_row=0)

        assert node_data.get("noble_standard") == "Enkel"

        display_lookup = {key: display for key, display, _ in fs.NOBLE_STANDARD_OPTIONS}
        standard_combo = _find_combobox_with_value(
            editor_frame, display_lookup["Enkel"]
        )
        assert standard_combo is not None
        assert standard_combo.get() == display_lookup["Enkel"]
    finally:
        root.destroy()


def test_creating_noble_child_updates_combobox_immediately():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        editor_frame = ttk.Frame(root)
        editor_frame.grid()

        sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
        sim.root = root
        sim.world_data = {
            "characters": {
                "1": {"name": "Lord", "gender": "Man"},
            },
            "nodes": {},
        }
        sim.add_status_message = lambda *_args, **_kwargs: None
        sim.save_current_world = lambda: None
        sim._open_character_editor = lambda *args, **kwargs: None
        sim._create_delete_button = lambda parent, *_args, **_kwargs: ttk.Button(
            parent, text="Radera"
        )
        sim.show_no_world_view = lambda: None
        sim.show_node_view = lambda node: None

        created_ids: list[int] = []

        def fake_creator(self, _node, callback, creation_context=None):
            new_id = 10 + len(created_ids)
            self.world_data["characters"][str(new_id)] = {
                "char_id": new_id,
                "name": f"Barn {new_id}",
                "gender": "Man",
            }
            created_ids.append(new_id)
            callback(new_id)

        sim._open_character_creator_for_node = types.MethodType(fake_creator, sim)

        node_data = {
            "node_id": 1,
            "noble_standard": "Välbärgad",
            "noble_lord": {"kind": "character", "char_id": 1},
            "noble_spouses": [{"kind": "placeholder", "label": ""}],
            "noble_spouse_children": [
                [{"kind": "placeholder", "label": "Barn levande"}]
            ],
            "noble_children": [{"kind": "placeholder", "label": "Barn levande"}],
            "noble_relatives": [],
        }

        sim._show_noble_family_editor(editor_frame, node_data, depth=0, start_row=0)

        child_combo = _find_combobox_with_value(editor_frame, "Barn levande")
        assert child_combo is not None, "Barn-kombo bör finnas"

        child_combo.set("Ny")
        child_combo.event_generate("<<ComboboxSelected>>")
        root.update_idletasks()

        assert created_ids, "Ny karaktär ska skapas"
        new_id = created_ids[0]

        expected_display = f"{new_id}: Barn {new_id}"
        updated_combo = _find_combobox_with_value(editor_frame, expected_display)
        assert updated_combo is not None, "Ny skapad karaktär ska visas"

        values = _combobox_values(updated_combo)
        display_value = updated_combo.get()
        assert expected_display in values
        assert display_value == expected_display
        assert str(new_id) in sim.world_data["characters"]
    finally:
        root.destroy()


def test_unavailable_noble_standard_resets_to_allowed_choice():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        editor_frame = ttk.Frame(root)
        editor_frame.grid()

        sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
        sim.root = root
        sim.world_data = {
            "characters": {},
            "nodes": {
                "1": {"node_id": 1, "parent_id": None},
                "2": {
                    "node_id": 2,
                    "parent_id": 1,
                    "res_type": "Byggnader",
                    "buildings": [{"type": "Trästuga 2 våningar", "count": 1}],
                },
            },
        }
        sim.add_status_message = lambda *_args, **_kwargs: None
        sim.save_current_world = lambda: None
        sim._open_character_editor = lambda *args, **kwargs: None
        sim._open_character_creator_for_node = lambda *args, **kwargs: None
        sim._create_delete_button = lambda parent, *_args, **_kwargs: ttk.Button(
            parent, text="Radera"
        )
        sim.show_no_world_view = lambda: None
        sim.show_node_view = lambda node: None

        node_data = {"node_id": 3, "parent_id": 1, "noble_standard": "Furstlig"}

        sim._show_noble_family_editor(editor_frame, node_data, depth=0, start_row=0)

        display_lookup = {key: display for key, display, _ in fs.NOBLE_STANDARD_OPTIONS}
        standard_combo = _find_combobox_with_value(
            editor_frame, display_lookup.get("Furstlig")
        )
        assert standard_combo is not None

        root.update_idletasks()

        assert standard_combo.get() == display_lookup["Anständig"]

        standard_combo.set(display_lookup["Furstlig"])
        root.update_idletasks()

        assert standard_combo.get() == display_lookup["Anständig"]
        assert node_data.get("noble_standard") == "Anständig"
    finally:
        root.destroy()


def test_creating_noble_relative_updates_combobox_immediately():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        editor_frame = ttk.Frame(root)
        editor_frame.grid()

        sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
        sim.root = root
        sim.world_data = {
            "characters": {
                "1": {"name": "Lord", "gender": "Man"},
            },
            "nodes": {},
        }
        sim.add_status_message = lambda *_args, **_kwargs: None
        sim.save_current_world = lambda: None
        sim._open_character_editor = lambda *args, **kwargs: None
        sim._create_delete_button = lambda parent, *_args, **_kwargs: ttk.Button(
            parent, text="Radera"
        )
        sim.show_no_world_view = lambda: None
        sim.show_node_view = lambda node: None

        created_ids: list[int] = []

        def fake_creator(self, _node, callback, creation_context=None):
            new_id = 20 + len(created_ids)
            self.world_data["characters"][str(new_id)] = {
                "char_id": new_id,
                "name": f"Släkting {new_id}",
                "gender": "Man",
            }
            created_ids.append(new_id)
            callback(new_id)

        sim._open_character_creator_for_node = types.MethodType(fake_creator, sim)

        node_data = {
            "node_id": 1,
            "noble_standard": "Välbärgad",
            "noble_lord": {"kind": "character", "char_id": 1},
            "noble_spouses": [],
            "noble_spouse_children": [],
            "noble_children": [],
            "noble_relatives": [
                {"kind": "placeholder", "label": "Släkting levande"}
            ],
        }

        sim._show_noble_family_editor(editor_frame, node_data, depth=0, start_row=0)

        relative_combo = _find_combobox_with_value(editor_frame, "Släkting levande")
        assert relative_combo is not None, "Släkting-kombo bör finnas"

        relative_combo.set("Ny")
        relative_combo.event_generate("<<ComboboxSelected>>")
        root.update_idletasks()

        assert created_ids, "Ny släkting ska skapas"
        new_id = created_ids[0]

        expected_display = f"{new_id}: Släkting {new_id}"
        updated_combo = _find_combobox_with_value(editor_frame, expected_display)
        assert updated_combo is not None, "Ny släkting ska visas"

        values = _combobox_values(updated_combo)
        display_value = updated_combo.get()
        assert expected_display in values
        assert display_value == expected_display
        assert str(new_id) in sim.world_data["characters"]
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


def test_noble_family_creation_blocked_without_buildings():
    world = {"nodes": {"1": {"node_id": 1, "parent_id": None}}, "characters": {}}
    sim = _make_sim_with_world_data(world)
    allowed, message = sim._evaluate_noble_family_placement({"node_id": 5, "parent_id": 1})

    assert allowed is False
    assert message == sim.NOBLE_FAMILY_MISSING_BUILDING_MSG


def test_noble_family_creation_blocked_when_family_already_exists():
    world = {
        "characters": {},
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "res_type": "Byggnader",
                "buildings": [{"type": "Stenhus", "count": 1}],
            },
            "3": {
                "node_id": 3,
                "parent_id": 1,
                "res_type": "Adelsfamilj",
                "noble_standard": "Enkel",
            },
        },
    }
    sim = _make_sim_with_world_data(world)

    allowed, message = sim._evaluate_noble_family_placement(
        {"node_id": 4, "parent_id": 1}
    )

    assert allowed is False
    assert message == sim.NOBLE_FAMILY_DUPLICATE_MSG


def test_noble_family_creation_allowed_with_valid_buildings():
    world = {
        "characters": {},
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "res_type": "Byggnader",
                "buildings": [{"type": "Borgkärna", "count": 1}],
            },
        },
    }
    sim = _make_sim_with_world_data(world)

    allowed, message = sim._evaluate_noble_family_placement(
        {"node_id": 3, "parent_id": 1}
    )

    assert allowed is True
    assert message is None


def test_building_change_blocked_when_family_standard_too_high():
    world = {
        "characters": {},
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "res_type": "Byggnader",
                "buildings": [{"type": "Borgkärna", "count": 1}],
            },
            "3": {
                "node_id": 3,
                "parent_id": 1,
                "res_type": "Adelsfamilj",
                "noble_standard": "Förnäm",
            },
        },
    }
    sim = _make_sim_with_world_data(world)
    node_data = world["nodes"]["2"]

    allowed, message = sim._validate_building_update(
        node_data, [{"type": "Stenhus", "count": 1}]
    )

    assert allowed is False
    assert message == sim.NOBLE_BUILDING_DOWNGRADE_MSG


def test_building_change_allowed_when_max_level_retained():
    world = {
        "characters": {},
        "nodes": {
            "1": {"node_id": 1, "parent_id": None},
            "2": {
                "node_id": 2,
                "parent_id": 1,
                "res_type": "Byggnader",
                "buildings": [
                    {"type": "Borgkärna", "count": 1},
                    {"type": "Trästuga liten", "count": 1},
                ],
            },
            "3": {
                "node_id": 3,
                "parent_id": 1,
                "res_type": "Adelsfamilj",
                "noble_standard": "Förnäm",
            },
        },
    }
    sim = _make_sim_with_world_data(world)
    node_data = world["nodes"]["2"]

    allowed, message = sim._validate_building_update(
        node_data, [{"type": "Borgkärna", "count": 1}]
    )

    assert allowed is True
    assert message is None


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


# --- Automatic character creation -------------------------------------------------


def test_open_character_creator_for_node_creates_character_without_editor():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {"characters": {"5": {"char_id": 5, "name": "Test", "gender": "Man"}}}

    saved = {"called": False}
    sim.add_status_message = lambda *_args, **_kwargs: None
    sim.save_current_world = lambda: saved.__setitem__("called", True)

    def fail(*_args, **_kwargs):
        raise AssertionError("Editor should not be opened for automatic characters")

    sim.show_edit_character_view = fail
    sim._generate_auto_character_name = lambda gender_code, _surname: f"auto-{gender_code}"

    created_ids: list[int] = []

    sim._open_character_creator_for_node({"node_id": 2}, lambda cid: created_ids.append(cid))

    assert created_ids, "Callback should be invoked with new character id"
    new_id = created_ids[0]
    assert new_id == 6
    assert str(new_id) in sim.world_data["characters"]
    assert sim.world_data["characters"][str(new_id)]["name"] == "auto-m"
    assert saved["called"]


def test_open_character_creator_for_node_spouse_inherits_surname_and_gender():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {
        "characters": {
            "10": {
                "char_id": 10,
                "name": "Karl av Test",
                "gender": "Man",
            }
        }
    }

    sim.add_status_message = lambda *_args, **_kwargs: None
    sim.save_current_world = lambda: None
    sim._node_display_name = lambda _node, _id: "Förläning"
    sim._generate_auto_character_name = (
        lambda gender_code, inherited_surname: f"{gender_code}:{inherited_surname or 'none'}"
    )

    node_data = {"node_id": 1, "noble_lord": {"kind": "character", "char_id": 10}}
    context = sim._make_relation_creation_context(node_data, "spouse")

    created_ids: list[int] = []
    sim._open_character_creator_for_node(
        node_data, lambda cid: created_ids.append(cid), creation_context=context
    )

    assert created_ids, "Expected automatic creation callback"
    new_id = created_ids[0]
    new_char = sim.world_data["characters"][str(new_id)]
    assert new_char["gender"] == "Kvinna"
    assert new_char["name"].endswith("Test")
    assert context["inherit_surname"] is True
