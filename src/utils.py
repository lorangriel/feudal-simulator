"""Utility functions used by the simulator."""
import random
import tkinter as tk
from tkinter import ttk

from constants import JARLDOM_RESOURCE_TYPES


def parse_int_10(value: str | int | None) -> int:
    """Return ``value`` parsed as a base-10 integer or 0 on failure."""
    try:
        text = str(value).strip()
    except Exception:
        return 0
    if not text:
        return 0
    try:
        return int(text, 10)
    except (ValueError, TypeError):
        return 0


def roll_dice(expr: str, debug=False):
    """Rolls dice based on standard notation (e.g., '3d6+2', 'ob2d6')."""
    expr_original = expr.strip()
    expr = expr_original.lower().strip()
    unlimited = False
    if expr.startswith("ob"):
        unlimited = True
        expr = expr[2:].strip()

    plus_mod = 0
    dice_part = expr
    if '+' in expr:
        parts = expr.split('+', 1)
        dice_part = parts[0].strip()
        try:
            plus_mod = int(parts[1].strip())
        except ValueError:
            return 0, f"Fel: Ogiltig modifierare i '{expr_original}'" if debug else ""

    if 'd' not in dice_part:
        # Allow just a modifier, e.g., "+5" which means "0d6+5"
        if expr_original.startswith('+'):
            try:
                res = int(expr_original)
                return res, f"Konstant {res}" if debug else ""
            except ValueError:
                pass  # Fall through to error
        return 0, f"Fel: saknar 'd' i '{expr_original}'" if debug else ""

    dparts = dice_part.split('d', 1)
    try:
        dice_count_str = dparts[0].strip()
        dice_count = 1 if not dice_count_str else int(dice_count_str)  # Handle "d6" as "1d6"
        die_type = int(dparts[1].strip())  # Usually 6 for Eon, but keep flexible
        if die_type <= 0:
            raise ValueError("Die type must be positive")
    except (ValueError, IndexError):
        return 0, f"Fel: Ogiltigt tärningsformat i '{expr_original}'" if debug else ""

    total = 0
    details = []
    if not unlimited:
        rolls = []
        for _ in range(dice_count):
            val = random.randint(1, die_type)
            rolls.append(val)
            total += val
        total += plus_mod
        if debug:
            dbg = f"Slår {dice_count}D{die_type} => {rolls} + {plus_mod} = {total}"
            return total, dbg
        return total, ""

    # Unlimited/Exploding dice
    queue = dice_count
    roll_count = 0
    while queue > 0 and roll_count < 100:
        val = random.randint(1, die_type)
        queue -= 1
        roll_count += 1
        if val == die_type:
            details.append(f"{die_type}->+2 nya")
            queue += 2
        else:
            details.append(str(val))
            total += val
    total += plus_mod
    if debug:
        dbg_rolls = ", ".join(details)
        if roll_count >= 100:
            dbg_rolls += " (MAX ROLLS)"
        dbg = f"Slår OB{dice_count}D{die_type} => [{dbg_rolls}] + {plus_mod} = {total}"
        return total, dbg
    return total, ""


def available_resource_types(world_data: dict | None, current_node_id: int | None = None) -> list[str]:
    """Return allowed resource types, hiding ``Väder`` if already in use."""
    options = list(JARLDOM_RESOURCE_TYPES)
    if not world_data:
        return options
    nodes = world_data.get("nodes", {})
    for nid, ndata in nodes.items():
        if ndata.get("res_type") == "Väder":
            try:
                if current_node_id is None or int(nid) != int(current_node_id):
                    options = [o for o in options if o != "Väder"]
                    break
            except Exception:
                if current_node_id is None or str(nid) != str(current_node_id):
                    options = [o for o in options if o != "Väder"]
                    break
    return options


def generate_swedish_village_name() -> str:
    """Generate a Swedish-sounding village name."""

    VANLIGA_FORLEDER = [
        "Björk", "Gran", "Lind", "Sjö", "Berg", "Älv", "Ek", "Tor", "Frej", "Ulf",
        "Sten", "Karl", "Erik", "Sig", "Ingrid", "Vik", "Olof", "Hög", "Räv", "Löv",
        "Orm", "Brunn", "Åker", "Arne", "Hilda", "Mjölk", "Fur", "Gull",
    ]

    OVANLIGA_FORLEDER = [
        "Troll", "Djupt", "Varg", "Vinter", "Silv", "Koppar", "Rim", "Lejon", "Gammel", "Hav",
    ]

    VANLIGA_EFTERLEDER = [
        "by", "torp", "hult", "ås", "rud", "vik", "näs", "tuna", "stad", "holm",
        "änge", "gård", "hed", "dal", "strand", "lid", "sjö", "träsk", "berga", "bro",
        "lunda", "klev", "backa", "ängen", "slätten", "forsen", "näset", "löten",
    ]

    OVANLIGA_EFTERLEDER = [
        "myra", "höjden", "torpet", "kärret", "udden", "klinten", "kulla", "skogen", "berget", "mark",
    ]

    PREFIX = [
        "Stora", "Lilla", "Norra", "Södra", "Övre", "Nedre", "Gamla", "Nya",
    ]

    def weighted_choice(vanliga, ovanliga, ovanlig_sannolikhet: float = 0.3):
        if random.random() < ovanlig_sannolikhet:
            return random.choice(ovanliga)
        return random.choice(vanliga)

    forled = weighted_choice(VANLIGA_FORLEDER, OVANLIGA_FORLEDER)
    efterled = weighted_choice(VANLIGA_EFTERLEDER, OVANLIGA_EFTERLEDER)

    if forled[-1] not in "aeiouyåäö" and random.random() < 0.35:
        mellanljud = random.choice(["e", "a", "i"])
        namn = forled + mellanljud + efterled
    else:
        namn = forled + efterled

    if random.random() < 0.08:
        prefix = random.choice(PREFIX)
        namn = f"{prefix} {namn}"

    return namn


def generate_character_name(gender: str = "m") -> str:
    """Return a random fantasy-style character name."""

    male_prefix = [
        "Ak",
        "Al",
        "An",
        "Ar",
        "Che",
        "Cor",
        "Dor",
        "Gar",
        "Gor",
        "Hal",
        "Hau",
        "Ig",
        "Ma",
        "Men",
        "Mik",
        "Nar",
        "Pal",
        "Pav",
        "Reh",
        "Sieg",
    ]

    male_suffix = [
        "an",
        "in",
        "on",
        "or",
        "os",
        "us",
        "am",
        "em",
        "en",
        "er",
        "el",
        "al",
        "il",
        "te",
        "as",
        "is",
        "rus",
        "vin",
        "vam",
        "val",
    ]

    female_prefix = [
        "An",
        "Des",
        "Dru",
        "Dol",
        "En",
        "Ef",
        "Gyn",
        "Gu",
        "Ine",
        "Iv",
        "Kat",
        "Len",
        "Mian",
        "Mon",
        "Nin",
        "Pat",
        "Sab",
        "Sel",
        "Van",
        "Vil",
    ]

    female_suffix = [
        "a",
        "ra",
        "na",
        "is",
        "ina",
        "ena",
        "ela",
        "ella",
        "ia",
        "va",
        "la",
        "e",
        "ae",
        "eni",
        "vi",
        "sa",
        "ta",
        "ni",
        "ma",
        "ya",
    ]

    if gender == "m":
        first = random.choice(male_prefix) + random.choice(male_suffix)
    else:
        first = random.choice(female_prefix) + random.choice(female_suffix)

    father = random.choice(male_prefix) + random.choice(male_suffix)
    return f"{first} {father}"


class ScrollableFrame(ttk.Frame):
    """A frame that adds a vertical scrollbar when content overflows."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.content = ttk.Frame(self.canvas)
        self.content.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)
        self.vscroll.pack(side=tk.RIGHT, fill="y")
        self._update_scrollbar()

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar()

    def _on_canvas_configure(self, event=None):
        self._update_scrollbar()

    def _update_scrollbar(self):
        if self.content.winfo_height() > self.canvas.winfo_height():
            if not self.vscroll.winfo_ismapped():
                self.vscroll.pack(side=tk.RIGHT, fill="y")
        else:
            if self.vscroll.winfo_ismapped():
                self.vscroll.pack_forget()
