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


def build_world(owner_with_province: int | None = None):
    nodes = {
        "1": {"node_id": 1, "parent_id": None, "children": [2]},
        "2": {"node_id": 2, "parent_id": 1, "children": [3]},
        "3": {"node_id": 3, "parent_id": 2, "children": [4]},
        "4": {"node_id": 4, "parent_id": 3, "children": []},
    }

    if owner_with_province is not None:
        nodes["4"]["owner_assigned_level"] = "2"
        nodes["4"]["owner_assigned_id"] = owner_with_province

    return {"nodes": nodes, "characters": {}}


def test_button_visible_and_disabled_without_provinces(root):
    app = ui_app.create_app(root)
    app.world_data = build_world(owner_with_province=None)
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("2")
    app.tree.focus("2")
    app.show_node_view(app.world_data["nodes"]["2"])

    assert app.personal_province_button is not None
    assert app.personal_province_button.instate(["disabled"])

    app.personal_province_button.invoke()
    assert app.current_province_owner_id is None
    assert app.structure_panel.mode == "admin"
    assert app.tree.heading("#0").get("text") == PANEL_NAMES["structure"]


def test_button_enabled_and_opens_province_view(root):
    app = ui_app.create_app(root)
    app.world_data = build_world(owner_with_province=3)
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("3")
    app.tree.focus("3")
    app.show_node_view(app.world_data["nodes"]["3"])

    assert app.personal_province_button is not None
    assert app.personal_province_button.instate(["!disabled"])

    app.personal_province_button.invoke()
    anchor = f"{FeodalSimulator.PROVINCE_ANCHOR_IID}3"

    assert app.tree.heading("#0").get("text") == STRUCTURE_ACTIONS["province_view"]
    assert app.current_province_owner_id == 3
    assert app.tree.get_children("") == (anchor,)


def test_no_button_for_depth_three(root):
    app = ui_app.create_app(root)
    app.world_data = build_world(owner_with_province=1)
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.show_node_view(app.world_data["nodes"]["4"])

    assert app.personal_province_button is None
