import random
import json

from time.time_engine import TimeEngine
from time.weather_lock import WeatherLock


def test_weather_is_locked_per_year():
    random.seed(42)
    engine = TimeEngine()
    weather_lock = WeatherLock()
    world = {}
    engine.record_change(world)

    for _ in range(4):
        engine.execute_current_year()

    engine.goto(5)
    year_five_weather = weather_lock.get_or_generate(5)
    world_with_weather = engine.get_current_snapshot()
    world_with_weather["weather"] = year_five_weather
    engine.record_change(world_with_weather)

    engine.goto(1)
    engine.goto(5)
    returned_weather = weather_lock.get_or_generate(5)
    assert returned_weather == year_five_weather
    assert engine.get_current_snapshot()["weather"] == year_five_weather


def test_weather_payload_is_json_serializable():
    weather_lock = WeatherLock()
    payload = weather_lock.get_or_generate(3)
    json_blob = json.dumps(payload, ensure_ascii=False)

    assert isinstance(payload, dict)
    assert "spring" in payload
    assert isinstance(json_blob, str)
