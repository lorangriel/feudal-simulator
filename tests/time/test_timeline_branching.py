from time.time_engine import TimeEngine


def test_branching_removes_future_and_rebuilds():
    engine = TimeEngine()
    world = {"value": 0}
    engine.record_change(world)

    for _ in range(10):
        engine.step(1)
        engine.record_change(world)

    engine.goto(0, 0)
    world["value"] = 1
    engine.record_change(world)

    assert all(key <= engine.current for key in engine.history)
    assert engine.max_future == engine.current
    assert engine.can_jump_decade() is False

    for _ in range(10):
        snapshot = engine.step(1)
        snapshot["value"] = engine.current[0] * 10 + engine.current[1]
        engine.record_change(snapshot)

    assert engine.max_future[0] >= 2
    assert engine.can_jump_decade() is True
    assert engine.history[engine.current]["value"] == engine.current[0] * 10 + engine.current[1]


def test_reset_timeline_restarts_history():
    engine = TimeEngine()
    engine.record_change({"value": 1})
    engine.step(1)
    engine.record_change({"value": 2})
    engine.reset_timeline(world_state={"value": 0})
    assert engine.current == (0, 0)
    assert engine.history[(0, 0)]["value"] == 0
