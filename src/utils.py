"""Utility functions used by the simulator."""
import random


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


def generate_swedish_village_name():
    """Generates a plausible Swedish-style place name."""
    FORLEDER = [
        "Björk", "Gran", "Lind", "Sjö", "Berg", "Älv", "Hav", "Hög", "Löv", "Ek",
        "Sten", "Sol", "Vind", "Ask", "Rönn", "Klipp", "Dal", "Sand", "Ler", "Moss",
        "Olof", "Erik", "Karl", "Ingrid", "Tor", "Frej", "Ulf", "Sig", "Arne", "Hilda",
        "Sven", "Astrid", "Björn", "Helga", "Sten", "Siv", "Ragnar", "Estrid", "Håkan",
        "Gunnar", "Liv", "Gertrud", "Bo", "Stig", "Svea", "Axel", "Alma",
    ]
    EFTERLEDER = [
        "by", "torp", "hult", "ås", "rud", "forsa", "vik", "näs", "tuna", "stad",
        "holm", "änge", "gård", "hed", "dal", "strand", "lid", "sjö", "träsk", "mark",
        "hem", "lösa", "köping", "berga", "lunda", "måla", "ryd", "rum", "sta", "landa",
    ]
    return random.choice(FORLEDER) + random.choice(EFTERLEDER)
