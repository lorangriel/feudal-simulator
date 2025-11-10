import runpy

from show_slots import main
from slot_display import CharacterSlotDisplay


def test_main_outputs_expected_display(capsys):
    expected = CharacterSlotDisplay().to_text() + "\n"
    main()
    captured = capsys.readouterr()
    assert captured.out == expected


def test_show_slots_script_entry(monkeypatch, capsys):
    monkeypatch.setattr(CharacterSlotDisplay, "to_text", lambda self: "SKRIV UT", raising=False)
    runpy.run_module("show_slots", run_name="__main__")
    captured = capsys.readouterr()
    assert captured.out.strip() == "SKRIV UT"
