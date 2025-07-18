"""Helper classes for querying equipment slot characteristics."""

from dataclasses import dataclass
from typing import Dict, List, Union

import item_defs


@dataclass(frozen=True)
class SlotCharacteristics:
    """Container for all attributes describing a slot."""

    index: int
    identifier: str
    name: str
    left_right: bool
    default_item: str
    is_armor: bool
    allow_additional_clothing: bool
    clothing_type: str
    tattooable: bool


class SlotHelper:
    """Provides convenient access to slot characteristics."""

    def __init__(self) -> None:
        self._slots: List[SlotCharacteristics] = []
        for i, identifier in enumerate(item_defs.SLOT_TYPES):
            self._slots.append(
                SlotCharacteristics(
                    index=i,
                    identifier=identifier,
                    name=item_defs.SLOT_NAMES[i],
                    left_right=item_defs.SLOT_LEFT_RIGHT[i],
                    default_item=item_defs.SLOT_ITEM[i],
                    is_armor=item_defs.SLOT_ARMOR[i],
                    allow_additional_clothing=item_defs.SLOT_ADDITIONAL_CLOTHING[i],
                    clothing_type=item_defs.CLOTHING_TYPES[i],
                    tattooable=item_defs.SLOT_TATTOO[i],
                )
            )
        self._by_name: Dict[str, SlotCharacteristics] = {
            slot.name: slot for slot in self._slots
        }
        self._by_identifier: Dict[str, SlotCharacteristics] = {
            slot.identifier: slot for slot in self._slots
        }

    def get(self, slot: Union[int, str]) -> SlotCharacteristics:
        """Return slot information by index, name or identifier."""
        if isinstance(slot, int):
            if slot < 0 or slot >= len(self._slots):
                raise IndexError(slot)
            return self._slots[slot]
        if slot in self._by_name:
            return self._by_name[slot]
        if slot in self._by_identifier:
            return self._by_identifier[slot]
        raise KeyError(slot)

    def all_slots(self) -> List[SlotCharacteristics]:
        """Return a list of all slot definitions."""
        return list(self._slots)
