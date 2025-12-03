import tkinter as tk
from types import SimpleNamespace

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


def build_world():
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2]},
            "2": {"node_id": 2, "parent_id": 1, "children": [3]},
            "3": {
                "node_id": 3,
                "parent_id": 2,
                "children": [],
                "owner_assigned_level": "1",
                "owner_assigned_id": 5,
            },
        },
        "characters": {},
    }


def test_admin_tree_shows_personal_icon_and_tooltip(root):
    app = ui_app.create_app(root)
    app.world_data = build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.item("1", open=True)
    app.tree.item("2", open=True)
    app.root.update_idletasks()

    assert "◆" in app.tree.item("3", "text")

    bbox = app.tree.bbox("3")
    assert bbox, "Tree item bbox should be available"
    mid_y = bbox[1] + bbox[3] // 2
    event = SimpleNamespace(y=mid_y)
    app.structure_panel._on_tree_motion(event)

    assert app.tooltip_manager._tooltips.get(app.tree) == "Personlig provins"
