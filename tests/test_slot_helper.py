import pytest

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


def test_get_slot_by_identifier():
    helper = SlotHelper()
    slot = helper.get("upper_lip")
    assert slot.identifier == "upper_lip"
    assert slot.name == "upper lip"


def test_get_slot_invalid_index_and_name():
    helper = SlotHelper()
    with pytest.raises(IndexError):
        helper.get(999)
    with pytest.raises(KeyError):
        helper.get("does-not-exist")

