import pytest

from src import feodal_simulator as fs
from src import population_utils as pu


class DummyText:
    """Minimal stand-in for a tkinter Text widget."""

    def __init__(self):
        self.content = ""
        self.state = "disabled"
        self.seen = False

    def config(self, state=None):
        if state is not None:
            self.state = state

    def insert(self, index, msg):
        self.content += msg

    def see(self, index):
        self.seen = True

    def get(self):
        return self.content


def test_calculate_population_from_fields():
    data = {
        "free_peasants": "2",
        "unfree_peasants": "3",
        "thralls": "1",
        "burghers": "4",
    }
    assert pu.calculate_population_from_fields(data) == 10
    assert pu.calculate_population_from_fields({"population": "7"}) == 7
    assert pu.calculate_population_from_fields({"population": "bad"}) == 0


def test_add_status_message_appends_and_disables():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.status_text = DummyText()
    fs.FeodalSimulator.add_status_message(sim, "hej")
    assert sim.status_text.get() == "hej\n"
    assert sim.status_text.state == "disabled"
    assert sim.status_text.seen


def test_commit_pending_changes_calls_callback_and_clears():
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    called = []

    def cb():
        called.append(True)

    sim.pending_save_callback = cb
    fs.FeodalSimulator.commit_pending_changes(sim)
    assert called
    assert sim.pending_save_callback is None


def test_save_current_world_updates_data_and_refreshes_map(monkeypatch):
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    world = {"nodes": {}, "characters": {}}
    sim.active_world_name = "A"
    sim.world_data = world
    sim.all_worlds = {}

    class DummyDM:
        def __init__(self):
            self.wd = None
            self.redrawn = False

        def set_world_data(self, wd):
            self.wd = wd

        def draw_dynamic_map(self):
            self.redrawn = True

    sim.dynamic_map_view = DummyDM()
    sim.refresh_dynamic_map = fs.FeodalSimulator.refresh_dynamic_map.__get__(sim)

    saved = {}

    def fake_save_worlds(data):
        saved["data"] = data

    monkeypatch.setattr(fs, "save_worlds_to_file", fake_save_worlds)

    fs.FeodalSimulator.save_current_world(sim)

    assert sim.all_worlds["A"] is world
    assert saved["data"]["A"] is world
    assert sim.dynamic_map_view.wd is world
    assert sim.dynamic_map_view.redrawn
