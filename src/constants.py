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
    "Härskare",
    # Settlement Types
    "By", "Stad", "Nybygge",
    # Animal Types
    "Stridshästar", "Ridhästar", "Packhästar", "Draghästar", "Oxe", "Föl",
    # Misc Countable Types
    "Jägare", "Båtar",
    # Building Types
    "Kvarn - vatten", "Kvarn - vind", "Bageri", "Smedja", "Garveri",
]

# Resource categories used for Jarldom-level holdings
JARLDOM_RESOURCE_TYPES = [
    "Gods",
    "Bosättning",
    "Vildmark",
    "Flod",
    "Hav",
    "Soldater",
    "Djur",
    "Karaktärer",
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
