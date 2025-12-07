import random

from time.time_engine import TimeEngine
from time.weather_lock import WeatherLock


def test_weather_is_locked_per_year():
    random.seed(42)
    engine = TimeEngine()
    weather_lock = WeatherLock()
    world = {}
    engine.record_change(world)

    for _ in range(5 * 4):
        snapshot = engine.step(1)
        engine.record_change(snapshot)

    year_five_weather = weather_lock.get_or_generate(5)
    world_with_weather = engine.get_current_snapshot()
    world_with_weather["weather"] = year_five_weather
    engine.record_change(world_with_weather)

    for _ in range(5 * 4):
        snapshot = engine.step(1)
        engine.record_change(snapshot)

    engine.goto(5, 0)
    returned_weather = weather_lock.get_or_generate(5)
    assert returned_weather == year_five_weather
    assert engine.get_current_snapshot()["weather"] == year_five_weather
