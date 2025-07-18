from slot_display import CharacterSlotDisplay


def test_contains_sections():
    display = CharacterSlotDisplay()
    text = display.to_text()
    assert "Armor" in text
    assert "Equipment" in text
    assert "Damage" in text
    assert "Damage Delivery" in text
