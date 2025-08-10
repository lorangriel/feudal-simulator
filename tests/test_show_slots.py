from show_slots import main
from slot_display import CharacterSlotDisplay


def test_main_outputs_expected_display(capsys):
    expected = CharacterSlotDisplay().to_text() + "\n"
    main()
    captured = capsys.readouterr()
    assert captured.out == expected
