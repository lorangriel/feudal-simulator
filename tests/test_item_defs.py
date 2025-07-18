from src import item_defs


def test_slot_lengths_consistent():
    assert len(item_defs.SLOT_TYPES) == len(item_defs.SLOT_NAMES) == len(item_defs.SLOT_LEFT_RIGHT)
    assert len(item_defs.SLOT_TYPES) == len(item_defs.SLOT_ITEM) == len(item_defs.SLOT_ARMOR)
    assert len(item_defs.SLOT_TYPES) == len(item_defs.SLOT_ADDITIONAL_CLOTHING) == len(item_defs.CLOTHING_TYPES)
    assert len(item_defs.SLOT_TYPES) == len(item_defs.SLOT_TATTOO)


def test_first_slot_example():
    assert item_defs.SLOT_NAMES[0] == "head"
    assert item_defs.SLOT_ITEM[0] == "helmet"
    assert item_defs.SLOT_ARMOR[0] is True
