import tkinter as tk

import pytest

from src.ui import app as ui_app


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


def test_combobox_visible_for_level_three_node(root):
    app = ui_app.create_app(root)
    app.world_data = {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [3]},
            "3": {"node_id": 3, "parent_id": 2, "children": [4]},
            "4": {"node_id": 4, "parent_id": 3, "children": []},
        }
    }
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    assert app.details_panel.ownership_frame.winfo_manager()
