"""Generate a textual representation of character equipment slots."""

from typing import List

import item_defs
from slot_helper import SlotHelper


class CharacterSlotDisplay:
    """Builds formatted descriptions of all equipment slots."""

    def __init__(self, helper: SlotHelper | None = None) -> None:
        self.helper = helper or SlotHelper()

    @staticmethod
    def _index_to_letter(index: int) -> str:
        """Return a single character label similar to C++ implementation."""
        return chr(ord("A") + index)

    def build_lines(self) -> List[str]:
        """Return a list of lines describing all slots and damage types."""
        lines: List[str] = []
        for armor in (True, False):
            lines.append("Armor" if armor else "Equipment")
            lines.append("---------")
            for slot in self.helper.all_slots():
                if slot.is_armor != armor:
                    continue
                letter = self._index_to_letter(slot.index)
                prefix = f"  [{letter}] "
                if slot.left_right:
                    base = f"Your right and left {slot.name} "
                else:
                    base = f"Your {slot.name} "
                pieces: List[str] = []
                if slot.default_item:
                    action = "equip" if armor else "wear"
                    part = f"may {action} one {slot.default_item}"
                    if slot.left_right:
                        part += " each"
                    pieces.append(part)
                if slot.clothing_type:
                    part = f"is able to wear one {slot.clothing_type}"
                    if slot.left_right:
                        part += " each"
                    pieces.append(part)
                if slot.tattooable:
                    pieces.append("can be tattooed")
                if not pieces:
                    pieces.append("just sits there")
                lines.append(prefix + base + ", and ".join(pieces) + ".")
            lines.append("")
        lines.append("Damage")
        lines.append("---------")
        for i, name in enumerate(item_defs.DAMAGE_TYPES):
            letter = self._index_to_letter(i)
            lines.append(f"  [{letter}] {name}")
        lines.append("")
        lines.append("Damage Delivery")
        lines.append("---------")
        for i, name in enumerate(item_defs.DAMAGE_DELIVERY_TYPES):
            letter = self._index_to_letter(i)
            lines.append(f"  [{letter}] {name}")
        return lines

    def to_text(self) -> str:
        """Return a single formatted string of the slot display."""
        return "\n".join(self.build_lines())
