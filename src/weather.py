from dataclasses import dataclass
import random


@dataclass(frozen=True)
class WeatherType:
    """Represents a weather category and its mechanical effects."""

    name: str
    production_percent: int
    hardship_modifier: int
    affected_industries: int


# Season-specific tables mapping roll ranges to weather types.
# Each entry is (min_roll, max_roll, WeatherType)
SPRING_WEATHER_TABLE = [
    (float("-inf"), 1, WeatherType("Storm och hagel (+3)", -25, 3, 4)),
    (2, 2, WeatherType("Våt och kall (+2)", -15, 2, 3)),
    (3, 3, WeatherType("Sen vår (+2)", -10, 2, 2)),
    (4, 4, WeatherType("Ostadig vår (+1)", -5, 1, 1)),
    (5, 9, WeatherType("Normal vår (±0)", 0, 0, 0)),
    (10, 10, WeatherType("Växlande sol (-1)", 1, -1, 1)),
    (11, 11, WeatherType("Varmt och stabilt (-1)", 2, -1, 2)),
    (12, 12, WeatherType("God växtkraft (-2)", 4, -2, 3)),
    (13, float("inf"), WeatherType("Exceptionellt vårväder (-3)", 8, -3, 4)),
]

SUMMER_WEATHER_TABLE = [
    (float("-inf"), 1, WeatherType("Torka och storm (+3)", -25, 3, 4)),
    (2, 2, WeatherType("Kvävande hetta (+2)", -15, 2, 3)),
    (3, 3, WeatherType("Torka (+2)", -10, 2, 2)),
    (4, 4, WeatherType("Nederbördsfattigt (+1)", -5, 1, 1)),
    (5, 9, WeatherType("Normal sommar (±0)", 0, 0, 0)),
    (10, 10, WeatherType("Måttlig värme (-1)", 1, -1, 1)),
    (11, 11, WeatherType("Soligt med regn (-1)", 2, -1, 2)),
    (12, 12, WeatherType("Stabil värme (-2)", 4, -2, 3)),
    (13, float("inf"), WeatherType("Idealisk sommar (-3)", 8, -3, 4)),
]

AUTUMN_WEATHER_TABLE = [
    (float("-inf"), 1, WeatherType("Ihållande regn (+3)", -25, 3, 4)),
    (2, 2, WeatherType("Tidig frost (+2)", -15, 2, 3)),
    (3, 3, WeatherType("Regn och blåst (+2)", -10, 2, 2)),
    (4, 4, WeatherType("Kyligt och blött (+1)", -5, 1, 1)),
    (5, 9, WeatherType("Normal höst (±0)", 0, 0, 0)),
    (10, 10, WeatherType("Lätt dimma (-1)", 1, -1, 1)),
    (11, 11, WeatherType("Klar höstluft (-1)", 2, -1, 2)),
    (12, 12, WeatherType("Soligt och torrt (-2)", 4, -2, 3)),
    (13, float("inf"), WeatherType("Perfekt skördväder (-3)", 8, -3, 4)),
]

WINTER_WEATHER_TABLE = [
    (float("-inf"), 1, WeatherType("Isstorm (+3)", -25, 3, 4)),
    (2, 2, WeatherType("Djup snö (+2)", -15, 2, 3)),
    (3, 3, WeatherType("Tidig snö (+2)", -10, 2, 2)),
    (4, 4, WeatherType("Snöslask (+1)", -5, 1, 1)),
    (5, 9, WeatherType("Normal vinter (±0)", 0, 0, 0)),
    (10, 10, WeatherType("Mild kyla (-1)", 1, -1, 1)),
    (11, 11, WeatherType("Lätt snö (-1)", 2, -1, 2)),
    (12, 12, WeatherType("Klart (-2)", 4, -2, 3)),
    (13, float("inf"), WeatherType("Torr och solig (-3)", 8, -3, 4)),
]

WEATHER_TABLES = {
    "spring": SPRING_WEATHER_TABLE,
    "summer": SUMMER_WEATHER_TABLE,
    "autumn": AUTUMN_WEATHER_TABLE,
    "winter": WINTER_WEATHER_TABLE,
}

NORMAL_WEATHER = {
    "spring": "Normal vår (±0)",
    "summer": "Normal sommar (±0)",
    "autumn": "Normal höst (±0)",
    "winter": "Normal vinter (±0)",
}


def get_weather_options(season: str) -> list[str]:
    """Return a list of weather names for the given ``season``."""
    return [wtype.name for _, _, wtype in WEATHER_TABLES[season]]


def determine_weather_type(total: int, season: str) -> WeatherType:
    """Return the WeatherType for ``total`` and ``season``."""
    table = WEATHER_TABLES.get(season, SPRING_WEATHER_TABLE)
    for low, high, wtype in table:
        if low <= total <= high:
            return wtype
    # Fallback, should never happen
    return WeatherType(NORMAL_WEATHER.get(season, "Normal vår (±0)"), 0, 0, 0)


def roll_weather(
    season: str, modifier: int = 0, rng: random.Random | None = None
) -> tuple[int, WeatherType]:
    """Roll 2d6 for ``season`` using ``rng`` (deterministic if supplied)."""

    roller = rng or random
    roll = roller.randint(1, 6) + roller.randint(1, 6)
    total = roll + modifier
    wtype = determine_weather_type(total, season)
    return total, wtype
