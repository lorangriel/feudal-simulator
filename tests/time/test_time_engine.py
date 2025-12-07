import pytest

from time.time_engine import TimeEngine


def test_year_listing_and_status():
    engine = TimeEngine()
    engine.record_change({"state": 1})

    years = engine.list_years()
    assert years == [1]
    entry = engine.get_year_entries()[0]
    assert entry.year == 1
    assert entry.status == TimeEngine.STATUS_PLANNING
    assert entry.selectable is True


def test_navigation_sticks_on_uncomputed():
    engine = TimeEngine()
    engine.record_change({"state": 1})

    engine.next_year()
    assert engine.current_year == 2
    assert engine.status(2) == TimeEngine.STATUS_PLANNING

    engine.prev_year()
    assert engine.current_year == 1
    engine.prev_year()
    assert engine.current_year == 1


def test_execute_locks_year_and_advance():
    engine = TimeEngine()
    engine.record_change({"val": 3})

    engine.execute_current_year()

    assert engine.is_computed(1) is True
    assert engine.current_year == 2
    assert engine.status(1) == TimeEngine.STATUS_LOCKED
    assert engine.status(2) == TimeEngine.STATUS_PLANNING


def test_ui_controls_follow_year_navigation(monkeypatch):
    try:
        import tkinter as tk
    except tk.TclError:
        pytest.skip("Tk not available")

    from feodal_simulator import FeodalSimulator

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    root.withdraw()
    sim = FeodalSimulator(root)
    sim.time_engine.reset_timeline(world_state={"nodes": {}}, start_year=1)
    sim._refresh_year_dropdown()

    sim._goto_next_year()
    assert sim.time_engine.current_year == 2
    sim._goto_previous_year()
    assert sim.time_engine.current_year == 1

    sim._execute_current_year()
    assert sim.time_engine.is_computed(1)
    assert sim.time_engine.current_year == 2
    root.destroy()
