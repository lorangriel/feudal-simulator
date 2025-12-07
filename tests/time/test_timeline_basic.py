import pytest

from time.time_engine import TimeEngine


def test_timeline_basic_snapshots_isolate_changes():
    engine = TimeEngine()
    world = {"nodes": {}}

    engine.record_change(world)
    engine.step(1)
    world_with_building = {"nodes": {"1": {"name": "Stuga"}}}
    engine.record_change(world_with_building)

    engine.goto(0, 0)
    initial_state = engine.get_current_snapshot()
    assert initial_state["nodes"] == {}

    engine.goto(0, 1)
    restored = engine.get_current_snapshot()
    assert restored["nodes"] == world_with_building["nodes"]


def test_current_position_and_missing_snapshots():
    engine = TimeEngine()
    engine.record_change({"state": 1})

    pos = engine.current_position
    assert pos.year == 0
    assert pos.season == 0

    engine.step(1)
    engine.record_change({"state": 2})

    with pytest.raises(ValueError):
        engine.goto(5, 0)


def test_step_wraps_to_previous_year():
    engine = TimeEngine()
    engine.record_change({"state": "start"})
    snapshot = engine.step(-1)
    assert engine.current == (-1, 3)
    assert snapshot["state"] == "start"
