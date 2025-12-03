import tkinter as tk

import pytest

from src.feodal_simulator import FeodalSimulator
from src.ui import app as ui_app
from src.ui.strings import PANEL_NAMES, STRUCTURE_ACTIONS


@pytest.fixture
def root():
    try:
        r = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk-display saknas, hoppar över UI-test")
    r.withdraw()
    yield r
    try:
        r.destroy()
    except tk.TclError:
        pass


def build_world(owner_id: int):
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [3]},
            "3": {"node_id": 3, "parent_id": 2, "children": [4, 5]},
            "4": {
                "node_id": 4,
                "parent_id": 3,
                "children": [],
                "owner_assigned_id": owner_id,
            },
            "5": {
                "node_id": 5,
                "parent_id": 3,
                "children": [],
                "owner_assigned_id": owner_id + 99,
            },
        },
        "characters": {},
    }


def test_province_view_toggles_and_filters(root):
    app = ui_app.create_app(root)
    app.world_data = build_world(owner_id=2)
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    anchor = f"{FeodalSimulator.PROVINCE_ANCHOR_IID}2"

    app.tree.selection_set("2")
    app.tree.focus("2")
    app.tree.item("1", open=True)
    app.tree.item("2", open=True)
    app.on_tree_selection_change()

    assert app.structure_panel.show_personal_button.winfo_manager()

    app.structure_panel.show_personal_button.invoke()
    assert app.tree.heading("#0").get("text") == STRUCTURE_ACTIONS["province_view"]

    visible_nodes = app.tree.get_children("")
    assert visible_nodes == (anchor,)
    assert app.tree.get_children(anchor) == ("4",)

    app.structure_panel.back_button.invoke()
    assert app.tree.heading("#0").get("text") == PANEL_NAMES["structure"]

    assert app.tree.exists("2")
    assert app.tree.selection() == ("2",)
    assert app.tree.item("2", "open")
    assert app.structure_panel.show_personal_button.winfo_manager()
