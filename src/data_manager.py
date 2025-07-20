"""Functions for loading and saving world data."""
import os
from tkinter import messagebox

from constants import DEFAULT_WORLDS_FILE
from world_interface import WorldInterface


def load_worlds_from_file():
    """Loads world data from the default JSON file."""
    if os.path.exists(DEFAULT_WORLDS_FILE):
        try:
            return WorldInterface.load_worlds_file(DEFAULT_WORLDS_FILE)
        except Exception as e:
            print(f"Error loading file {DEFAULT_WORLDS_FILE}: {e}")
            messagebox.showerror(
                "Laddningsfel",
                f"Ett oväntat fel uppstod vid läsning av {DEFAULT_WORLDS_FILE}.\n\n{e}",
            )
            return {}
    return {}


def save_worlds_to_file(all_worlds):
    """Saves all world data to the default JSON file."""
    try:
        WorldInterface.save_worlds_file(all_worlds, DEFAULT_WORLDS_FILE)
    except Exception as e:
        print(f"Error saving file {DEFAULT_WORLDS_FILE}: {e}")
        messagebox.showerror(
            "Sparfel",
            f"Kunde inte spara data till {DEFAULT_WORLDS_FILE}.\n\n{e}",
        )

