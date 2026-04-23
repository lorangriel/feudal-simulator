import random
from typing import Dict

from weather import roll_weather

SEASONS = ("spring", "summer", "autumn", "winter")


class WeatherLock:
    def __init__(self):
        # year → season-to-weather-name mapping
        self.weather: Dict[int, Dict[str, str]] = {}

    def get_or_generate(self, year: int):
        """
        Return existing weather for the year, or
        generate 4 results and store permanently.
        """

        if year in self.weather:
            return self.weather[year]
        rng = random.Random(year)
        generated = {
            season: roll_weather(season, rng=rng)[1].name for season in SEASONS
        }
        self.weather[year] = generated
        return generated
