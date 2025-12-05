import tkinter as tk
from tkinter import messagebox

import pytest

from src.events import PROVINCE_OWNER_CHANGED
from src.ui import app as ui_app


@pytest.fixture
def root(monkeypatch):
    try:
        r = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk-display saknas, hoppar över UI-test")
    r.withdraw()
    monkeypatch.setattr(messagebox, "showerror", lambda *args, **kwargs: None)
    yield r
    try:
        r.destroy()
    except tk.TclError:
        pass


def build_world(owner_level: str = "none", owner_id: int | None = None):
    return {
        "nodes": {
            "1": {"node_id": 1, "parent_id": None, "children": [2], "name": "Sveariket"},
            "2": {"node_id": 2, "parent_id": 1, "children": [3], "name": "Uppland"},
            "3": {"node_id": 3, "parent_id": 2, "children": [4], "name": "Attundaland"},
            "4": {
                "node_id": 4,
                "parent_id": 3,
                "children": [],
                "custom_name": "Testdalen",
                "owner_assigned_level": owner_level,
                "owner_assigned_id": owner_id,
                "personal_province_path": [1, 2] if owner_level != "none" else [],
            },
        }
    }


def test_structure_refreshes_after_owner_change(root):
    app = ui_app.create_app(root)
    app.world_data = build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    events: list[dict] = []
    app.event_bus.on(PROVINCE_OWNER_CHANGED, lambda **payload: events.append(payload))

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    owner_label = f"Furstendömet {app.get_display_name(2)}"
    app.details_panel.ownership_combobox.set(owner_label)
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    assert len(events) == 1
    assert app.tree.selection() == ("4",)
    assert app.tree.item("1", "open") is True
    assert app.tree.item("2", "open") is True
    assert "personal_province" in app.tree.item("4", "tags")
    assert any("Struktur uppdaterad" in msg for msg in app.status_service.messages)
