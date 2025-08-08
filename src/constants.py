# -*- coding: utf-8 -*-
"""Shared constants and resource definitions for the simulator."""

# Default file used for saving/loading world data
DEFAULT_WORLDS_FILE = "worlds.json"

# Resource types
RES_TYPES = [
    "Resurs",  # Generic/Default
    # Areal Types
    "Jaktmark", "Odlingsmark", "Betesmark", "Fiskevatten",
    # Soldier Types
    "Armborstskytt", "Bågskytt", "Långbågskytt", "Fotsoldat", "Fotsoldat - lätt",
    "Fotsoldat - tung", "Marinsoldat", "Sjöman",
    # Character Types (People resources, often singular with ruler)
    "Officer", "Riddare med väpnare", "Falkenerare", "Fogde", "Härold",
    "Livmedikus", "Förvaltare", "Duvhanterare", "Malmletare", "Munskänk",
    "Jägarmästare",
    "Härskare",
    # Settlement Types
    "By", "Stad", "Nybygge",
    # Animal Types
    "Stridshästar", "Ridhästar", "Packhästar", "Draghästar", "Oxe", "Föl",
    # Misc Countable Types
    "Jägare", "Båtar",
    # Building Types
    "Kvarn - vatten", "Kvarn - vind", "Bageri", "Smedja", "Garveri",
    # Storage Type
    "Lager",
]

# Resource categories used for Jarldom-level holdings
JARLDOM_RESOURCE_TYPES = [
    "Gods",
    "Bosättning",
    "Vildmark",
    "Jaktmark",
    "Mark",
    "Flod",
    "Hav",
    "Soldater",
    "Djur",
    "Karaktärer",
    "Byggnader",
    "Väder",
    "Lager",
]

# Categorized for easier handling in UI
AREAL_TYPES = {"Jaktmark", "Odlingsmark", "Betesmark", "Fiskevatten"}
SOLDIER_TYPES = {
    "Armborstskytt", "Bågskytt", "Långbågskytt", "Fotsoldat", "Fotsoldat - lätt",
    "Fotsoldat - tung", "Marinsoldat", "Sjöman"
}
CHARACTER_TYPES = {
    "Officer", "Riddare med väpnare", "Falkenerare", "Fogde", "Härold",
    "Livmedikus", "Förvaltare", "Duvhanterare", "Malmletare", "Munskänk",
    "Jägarmästare",
    "Härskare"
}
SETTLEMENT_TYPES = {"By", "Stad", "Nybygge"}
ANIMAL_TYPES = {"Stridshästar", "Ridhästar", "Packhästar", "Draghästar", "Oxe", "Föl"}
MISC_COUNT_TYPES = {"Jägare", "Båtar"}
BUILDING_TYPES = {"Kvarn - vatten", "Kvarn - vind", "Bageri", "Smedja", "Garveri"}

# Example list of possible craftsman professions for settlement UI
CRAFTSMAN_TYPES = [
    "Smed",
    "Snickare",
    "Bagare",
    "Skräddare",
    "Bryggare",
    "Skomakare",
    "Korgmakare",
    "Timmerman",
    "Målare",
]

# Border types for neighbors
BORDER_TYPES = [
    "<Ingen>", "liten väg", "väg", "stor väg", "vildmark", "träsk", "berg", "vattendrag"
]
DEFAULT_BORDER_TYPE = "vildmark"  # Default when adding via map drag
BORDER_COLORS = {
    "<Ingen>": "gray",
    "liten väg": "saddle brown",  # Distinct road colors
    "väg": "peru",
    "stor väg": "darkred",
    "vildmark": "darkgreen",
    "träsk": "olive drab",
    "berg": "dimgray",
    "vattendrag": "royalblue",
}
NEIGHBOR_NONE_STR = "<Ingen>"
NEIGHBOR_OTHER_STR = "Annat land"
MAX_NEIGHBORS = 6

# Currently unused cost of living levels
LEVNADSKOSTNADER = [
    "Nödtorftigt leverne",
    "Gement leverne",
    "Gott leverne",
    "Mycket gott leverne",
    "Lyxliv",
]

# Work duty levels used for jarldoms
DAGSVERKEN_LEVELS = [
    "inga",
    "få",
    "normalt",
    "många",
    "tyranniskt många",
]

# Mapping from dagsverken level to work days per unfree peasant
DAGSVERKEN_MULTIPLIERS = {
    "inga": 0,
    "få": 40,
    "normalt": 80,
    "många": 100,
    "tyranniskt många": 120,
}

# Umbärande modifiers for each dagsverken level
DAGSVERKEN_UMBARANDE = {
    "inga": -2,
    "få": -1,
    "normalt": 0,
    "många": 1,
    "tyranniskt många": 2,
}

# Work days produced by a single thrall
THRALL_WORK_DAYS = 300

# Work days produced by a single day laborer
DAY_LABORER_WORK_DAYS = 70

# Fish quality levels for sea and river resources
FISH_QUALITY_LEVELS = [
    "Kassat",
    "mindre bra",
    "Normalt",
    "ganska bra",
    "bäst",
]

# Maximum number of fishing boats allowed
MAX_FISHING_BOATS = 20
