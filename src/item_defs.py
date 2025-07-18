# -*- coding: utf-8 -*-
"""Equipment slot and damage type definitions ported from the C++ version.

This module provides constants describing character equipment slots and
weapon damage types. It mirrors the data found in ``item.h`` so it can be
used by the Python implementation of the feudal simulator.
"""

# Equipment slot identifiers in the original order
SLOT_TYPES = [
    "head", "ear", "nose", "upper_lip", "lower_lip", "shoulder", "upper_arm",
    "lower_arm", "hand", "thumb", "index_finger", "middle_finger",
    "ring_finger", "pinky", "neck", "throat", "chest", "back", "hip",
    "crotch", "upper_leg", "lower_leg", "foot", "big_toe", "second_toe",
    "third_toe", "fourth_toe", "fifth_toe", "waist", "lower_body", "ankle",
    "wrist", "forehead", "cheek", "chin", "upper_body", "mouth", "nostril",
    "shoulderblade", "shoulders",
]

# Human readable names for the slots
SLOT_NAMES = [
    "head", "ear", "nose", "upper lip", "lower lip", "shoulder", "upper arm",
    "lower arm", "hand", "thumb", "index finger", "middle finger",
    "ring finger", "pinky", "neck", "throat", "chest", "back", "hip",
    "crotch", "upper leg", "lower leg", "foot", "big toe", "second toe",
    "third toe", "fourth toe", "fifth toe", "waist", "lower body", "ankle",
    "wrist", "forehead", "cheek", "chin", "upper body", "mouth", "nostril",
    "shoulderblade", "shoulders",
]

# Whether each slot comes in a left/right pair
SLOT_LEFT_RIGHT = [
    False, True, False, True, True, True, True, True,
    True, True, True, True, True, True, False, False,
    False, False, True, False, True, True, True, True,
    True, True, True, True, False, False, True, True,
    False, True, False, False, False, True, True, False,
]

# Default item that can be equipped on the slot (may be empty)
SLOT_ITEM = [
    "helmet", "earring", "nose ring", "lip piercing", "lip piercing",
    "shoulder pad", "upper arm protection", "lower arm protection",
    "gauntlet", "ring", "ring", "ring", "ring", "ring",
    "neck protection", "necklace", "", "", "pouch", "crotch protection",
    "upper leg protection", "lower leg protection", "shoe", "ring",
    "ring", "ring", "ring", "ring", "belt", "lower body protection",
    "bracelet", "bracelet", "", "", "", "upper body protection",
    "mouth cover", "piercing", "quiver", "backpack",
]

# Whether the default item for the slot counts as armour
SLOT_ARMOR = [
    True, False, False, False, False, True, True, True,
    True, False, False, False, False, False, True, False,
    False, False, False, True, True, True, True, False,
    False, False, False, False, False, True, False, False,
    False, False, False, True, False, False, False, False,
]

# Some slots allow additional clothing items
SLOT_ADDITIONAL_CLOTHING = [
    True, False, True, False, False, False, False, False,
    True, False, False, False, False, False, True, False,
    False, True, False, False, False, False, False, False,
    False, False, False, False, False, True, False, False,
    False, False, False, True, False, False, False, False,
]

# Types of clothing that can occupy a slot (may be empty)
CLOTHING_TYPES = [
    "hat", "", "nose cap", "", "", "", "", "",
    "glove", "", "", "", "", "", "scarf", "",
    "", "cloak", "", "", "", "", "", "",
    "", "", "", "", "", "pair of trousers", "", "",
    "", "", "", "shirt", "", "", "", "",
]

# Whether the slot can be tattooed
SLOT_TATTOO = [
    False, False, False, False, False, False, True, True,
    True, False, False, False, False, False, True, False,
    True, True, False, False, True, True, True, False,
    False, False, False, False, False, False, True, True,
    True, True, False, False, False, False, False, False,
]

# Damage and weapon related constants
DAMAGE_DELIVERY_TYPES = ["melee", "projectile", "beam"]
DAMAGE_TYPES = [
    "kinetic", "electric", "magnetic", "particle", "laser", "sound",
    "elemental", "dark", "fire", "ice", "magic", "mental",
]
