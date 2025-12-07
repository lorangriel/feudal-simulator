import random
from typing import Dict, Tuple

from weather import roll_weather


class WeatherLock:
    def __init__(self):
        # year → 4-season weather tuple
        self.weather: Dict[int, Tuple] = {}

    def get_or_generate(self, year: int):
        """
        Return existing weather for the year, or
        generate 4 results and store permanently.
        """

        if year in self.weather:
            return self.weather[year]
        generated = tuple(roll_weather(random.Random(year)) for _ in range(4))
        self.weather[year] = generated
        return generated
