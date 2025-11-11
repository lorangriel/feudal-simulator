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
        assert tab_texts == ["Gemål", "Släktingar"]

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

        spouse_texts = collect_texts(spouse_tab_widget)
        assert "Gemål:" in spouse_texts

        relatives_texts = collect_texts(relatives_tab_widget)
        assert "Barn:" in relatives_texts
        assert "Släktingar:" in relatives_texts
    finally:
        root.destroy()
