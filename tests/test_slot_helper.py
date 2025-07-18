from slot_helper import SlotHelper


def test_get_slot_by_name():
    helper = SlotHelper()
    slot = helper.get("head")
    assert slot.name == "head"
    assert slot.default_item == "helmet"
    assert slot.is_armor is True


def test_get_slot_by_index():
    helper = SlotHelper()
    slot0 = helper.get(0)
    slot1 = helper.get(1)
    assert slot0.identifier == "head"
    assert slot1.identifier == "ear"

