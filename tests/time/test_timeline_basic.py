from time.time_engine import TimeEngine


def test_snapshots_are_preserved_when_planning_changes():
    engine = TimeEngine()
    engine.record_change({"value": 1})
    engine.execute_current_year()

    assert engine.history[1]["value"] == 1

    engine.prev_year()
    past_state = engine.get_current_snapshot()
    past_state["value"] = 2
    engine.record_change(past_state)

    assert engine.history[1]["value"] == 1
    assert engine.planning_state[1]["value"] == 2
