"""Random name generation utilities."""
import random


class NameRandomizer:
    """Generates random names using simple prefix/suffix lists."""

    def __init__(self):
        # Beginning parts of the names, ported from MobFactory.cpp
        self.name_beg = [
            "naz",
            "mor",
            "gnar",
            "aahr",
            "more",
            "dark",
            "bam",
            "raab",
            "rake",
            "lor",
            "smur",
        ]

        # Ending parts of the names
        self.name_end = [
            "guz",
            "kill",
            "gul",
            "gok",
            "tan",
            "tok",
            "bul",
            "zod",
            "zed",
            "dor",
            "grim",
            "yohn",
            "fan",
        ]

    def random_name(self) -> str:
        """Return a capitalized random name built from the prefix/suffix lists."""
        name = random.choice(self.name_beg) + random.choice(self.name_end)
        return name.capitalize()
