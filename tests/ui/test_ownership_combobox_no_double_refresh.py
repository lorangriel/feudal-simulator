import tkinter as tk
from tkinter import messagebox

import pytest

from src.events import PROVINCE_OWNER_CHANGED
from src.ui import app as ui_app
from src.world_manager import AssignResult


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


def test_owner_change_refreshes_once_via_event(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    refresh_calls: list[int | str] = []
    original_refresh = app.structure_view.refresh_after_owner_change

    def _refresh_spy(province_id):
        refresh_calls.append(province_id)
        return original_refresh(province_id)

    monkeypatch.setattr(app.structure_view, "refresh_after_owner_change", _refresh_spy)

    events: list[dict] = []
    app.event_bus.on(PROVINCE_OWNER_CHANGED, lambda **payload: events.append(payload))

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    owner_label = f"Furstendömet {app.get_display_name(2)}"
    app.details_panel.ownership_combobox.set(owner_label)
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    assert len(refresh_calls) == 1
    assert len(events) == 1


def test_no_refresh_when_assignment_is_unchanged(root, monkeypatch):
    app = ui_app.create_app(root)
    app.world_data = build_world()
    app.world_manager.set_world_data(app.world_data)
    app.populate_tree()

    refresh_calls: list[int | str] = []
    monkeypatch.setattr(
        app.structure_view,
        "refresh_after_owner_change",
        lambda province_id: refresh_calls.append(province_id),
    )

    events: list[dict] = []
    app.event_bus.on(PROVINCE_OWNER_CHANGED, lambda **payload: events.append(payload))

    def _no_change_assign(_province_id, _owner_anchor):
        return AssignResult(
            True,
            "Ingen ändring",
            owner_level="none",
            owner_id=None,
            personal_path=[],
            changed=False,
        )

    monkeypatch.setattr(app.world_manager, "assign_personal_owner", _no_change_assign)

    app.tree.selection_set("4")
    app.tree.focus("4")
    app.on_tree_selection_change()

    owner_label = f"Furstendömet {app.get_display_name(2)}"
    app.details_panel.ownership_combobox.set(owner_label)
    app.details_panel.ownership_combobox.event_generate("<<ComboboxSelected>>")

    assert not refresh_calls
    assert not events
    assert not any(
        "Ägare uppdaterad" in msg or "Struktur uppdaterad" in msg
        for msg in app.status_service.messages
    )
