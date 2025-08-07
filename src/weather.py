from dataclasses import dataclass
import random


@dataclass(frozen=True)
class WeatherType:
    """Represents a weather category and its mechanical effects."""

    name: str
    production_percent: int
    hardship_modifier: int
    affected_industries: int


# Table mapping roll ranges to weather types.
# Each entry is (min_roll, max_roll, WeatherType)
WEATHER_TABLE = [
    (float("-inf"), 1, WeatherType("Ödeläggelse", -25, 3, 4)),
    (2, 2, WeatherType("Storm", -15, 2, 3)),
    (3, 3, WeatherType("Oväder", -10, 2, 2)),
    (4, 4, WeatherType("Ostadighet", -5, 1, 1)),
    (5, 9, WeatherType("Normalväder", 0, 0, 0)),
    (10, 10, WeatherType("Gynnsamhet", 1, -1, 1)),
    (11, 11, WeatherType("Solsken", 2, -1, 2)),
    (12, 12, WeatherType("Fruktbarhet", 4, -2, 3)),
    (13, float("inf"), WeatherType("Mirakelväder", 8, -3, 4)),
]


def determine_weather_type(total: int) -> WeatherType:
    """Return the WeatherType corresponding to ``total``."""
    for low, high, wtype in WEATHER_TABLE:
        if low <= total <= high:
            return wtype
    # Fallback, should never happen
    return WeatherType("Normalväder", 0, 0, 0)


def roll_weather(modifier: int = 0) -> tuple[int, WeatherType]:
    """Roll 2d6, apply ``modifier`` and return the resulting WeatherType."""
    roll = random.randint(1, 6) + random.randint(1, 6)
    total = roll + modifier
    wtype = determine_weather_type(total)
    return total, wtype
