import tkinter as tk

import pytest

from src.feodal_simulator import FeodalSimulator
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


def build_world(owner_id: int, owner_name: str):
    return {
        "nodes": {
            str(owner_id): {
                "node_id": owner_id,
                "parent_id": None,
                "children": [200],
                "name": owner_name,
            },
            "200": {"node_id": 200, "parent_id": owner_id, "children": [201]},
            "201": {"node_id": 201, "parent_id": 200, "children": []},
        },
        "characters": {},
    }


def test_owner_anchor_renders_and_hosts_subtree(root):
    owner_id = 2
    app = ui_app.create_app(root)
    app.world_data = build_world(owner_id, owner_name="Ägarnamn")
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.get_province_subtree = lambda _owner_id: [
        {"id": 200, "children": [{"id": 201, "children": []}]}
    ]

    anchor = f"{FeodalSimulator.PROVINCE_ANCHOR_IID}{owner_id}"

    app.tree.selection_set(str(owner_id))
    app.tree.focus(str(owner_id))
    app.on_tree_selection_change()

    app.structure_panel.show_personal_button.invoke()

    assert app.tree.exists(anchor)
    assert app.tree.item(anchor, "text").startswith("Ägare:")
    assert app.tree.get_children("") == (anchor,)
    assert app.tree.get_children(anchor) == ("200",)
    assert app.tree.get_children("200") == ("201",)


def test_owner_anchor_renders_without_subtree(root):
    owner_id = 3
    app = ui_app.create_app(root)
    app.world_data = build_world(owner_id, owner_name="Tomt ägande")
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.get_province_subtree = lambda _owner_id: []

    anchor = f"{FeodalSimulator.PROVINCE_ANCHOR_IID}{owner_id}"

    app.tree.selection_set(str(owner_id))
    app.tree.focus(str(owner_id))
    app.on_tree_selection_change()

    app.structure_panel.show_personal_button.invoke()

    assert app.tree.exists(anchor)
    assert app.tree.get_children("") == (anchor,)
    assert app.tree.get_children(anchor) == ()
    assert app.tree.item(anchor, "text").startswith("Ägare:")
