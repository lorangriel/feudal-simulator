import types

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
