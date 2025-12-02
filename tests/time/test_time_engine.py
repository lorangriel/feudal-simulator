import tkinter as tk

import pytest

from feodal_simulator import FeodalSimulator
from time_engine import SEASONS, TimeEngine, TimePosition, rng_for


def _order_processor(engine: TimeEngine, pos: TimePosition, rng):
    key = f"{pos.year}-{pos.season}"
    orders = engine.world_state.get("orders", {})
    if key in orders:
        engine.world_state["order_total"] = engine.world_state.get("order_total", 0) + orders[key]
        engine._events.append({"type": "order_applied", "key": key, "delta": orders[key]})


def test_deterministic_snapshots(tmp_path):
    base_state = {"resource": 1}
    engine_a = TimeEngine(
        timeline_id="det", rng_seed=99, world_state=base_state, base_path=tmp_path / "a"
    )
    engine_b = TimeEngine(
        timeline_id="det", rng_seed=99, world_state=base_state, base_path=tmp_path / "b"
    )

    for _ in range(8):
        engine_a.step_seasons(1)
        engine_b.step_seasons(1)

    checks_a = [snap["checksum"] for snap in engine_a.snapshots]
    checks_b = [snap["checksum"] for snap in engine_b.snapshots]
    assert checks_a == checks_b


@pytest.mark.parametrize("start_year", [0, 3])
def test_year_vs_season_steps(tmp_path, start_year):
    engine = TimeEngine(timeline_id=f"step-{start_year}", base_path=tmp_path)
    engine.step_seasons(start_year * len(SEASONS))
    pos_four = engine.step_seasons(4)
    engine.reset_timeline(world_state=engine.world_state, timeline_id=f"step-{start_year}-b")
    engine.step_seasons(start_year * len(SEASONS))
    pos_year = engine.step_seasons(4)
    assert pos_four == pos_year
    back = engine.step_seasons(-4)
    assert back.year == pos_four.year - 1


def test_snapshot_restore_and_orders(tmp_path):
    state = {"orders": {"3-autumn": 5, "7-summer": 2}}
    engine = TimeEngine(
        timeline_id="orders", base_path=tmp_path, world_state=state, season_processors=[
            lambda eng, pos, rng: eng._run_weather(eng, pos, rng),
            _order_processor,
        ]
    )
    target = TimePosition.from_season(3, "autumn")
    engine.step_to(target)
    autumn_checksum = engine.snapshots[-1]["checksum"]
    assert engine.world_state.get("order_total", 0) == 5

    engine.step_to(TimePosition.from_season(7, "summer"))
    assert engine.world_state.get("order_total", 0) == 7

    engine.step_to(target)
    restored = next(
        snap for snap in reversed(engine.snapshots) if snap["year"] == 3 and snap["season"] == "autumn"
    )
    assert restored["checksum"] == autumn_checksum
    assert engine.world_state.get("order_total", 0) == 5


def test_rng_for_weather_is_deterministic():
    rng = rng_for("abc", 2, "spring", node_id=1, subsystem_tag="weather", base_seed=7)
    vals = [rng.randint(1, 6) for _ in range(4)]
    rng2 = rng_for("abc", 2, "spring", node_id=1, subsystem_tag="weather", base_seed=7)
    assert vals == [rng2.randint(1, 6) for _ in range(4)]


def test_ui_buttons_drive_time(tmp_path):
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("Tk not available")
    sim = FeodalSimulator(root)
    sim.time_engine.reset_timeline(world_state={}, timeline_id="ui-test", rng_seed=1)
    sim._update_time_label(sim.time_engine.current_position)
    sim.step_time(1)
    assert sim.time_engine.current_position.season == "summer"
    sim.step_time(3)
    assert sim.time_engine.current_position.year == 1
    assert sim.time_engine.current_position.season == "spring"
    root.destroy()
