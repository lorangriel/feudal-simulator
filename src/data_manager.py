"""Functions for loading and saving world data."""
import json
import os
from tkinter import messagebox

from constants import DEFAULT_WORLDS_FILE


def load_worlds_from_file():
    """Loads world data from the default JSON file."""
    if os.path.exists(DEFAULT_WORLDS_FILE):
        try:
            with open(DEFAULT_WORLDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {DEFAULT_WORLDS_FILE}: {e}")
            messagebox.showerror(
                "Laddningsfel",
                f"Kunde inte läsa filen {DEFAULT_WORLDS_FILE}.\nFilen kan vara korrupt.\n\n{e}",
            )
            return {}
        except Exception as e:
            print(f"Error loading file {DEFAULT_WORLDS_FILE}: {e}")
            messagebox.showerror(
                "Laddningsfel",
                f"Ett oväntat fel uppstod vid läsning av {DEFAULT_WORLDS_FILE}.\n\n{e}",
            )
            return {}
    else:
        return {}


def save_worlds_to_file(all_worlds):
    """Saves all world data to the default JSON file."""
    try:
        with open(DEFAULT_WORLDS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_worlds, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving file {DEFAULT_WORLDS_FILE}: {e}")
        messagebox.showerror(
            "Sparfel",
            f"Kunde inte spara data till {DEFAULT_WORLDS_FILE}.\n\n{e}",
        )

