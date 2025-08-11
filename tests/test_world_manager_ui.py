from src.world_manager_ui import WorldManagerUI


def test_save_current_world_updates_and_refreshes(monkeypatch):
    saved = {}

    def fake_save(data):
        saved["data"] = data

    ui = WorldManagerUI(save_func=fake_save)
    all_worlds = {}
    world = {"nodes": {}, "characters": {}}
    refreshed = []

    def refresh():
        refreshed.append(True)

    ui.save_current_world("A", world, all_worlds, refresh)

    assert all_worlds["A"] is world
    assert saved["data"] is all_worlds
    assert refreshed
