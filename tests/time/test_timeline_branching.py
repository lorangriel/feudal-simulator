from time.time_engine import TimeEngine


def test_goto_creates_planning_state_and_respects_floor():
    engine = TimeEngine(start_year=1)
    engine.record_change({"v": 1})

    engine.goto(3)
    assert engine.current_year == 3
    assert engine.status(3) == TimeEngine.STATUS_PLANNING
    assert 3 in engine.planning_state

    engine.goto(0)
    assert engine.current_year == 1
