import runpy

from generate_names import main
from name_randomizer import NameRandomizer


def test_main_prints_deterministic_names(capsys):
    rand = NameRandomizer(seed=123)
    expected = rand.generate_names(count=10)

    main(count=10, seed=123)
    captured = capsys.readouterr()
    output = captured.out.strip().splitlines()
    assert output == expected
    assert len(output) == 10


def test_generate_names_script_entry(monkeypatch, capsys):
    calls = {}

    def fake_generate(self, count=50):
        calls["count"] = count
        return [f"namn-{i}" for i in range(count)]

    monkeypatch.setattr(NameRandomizer, "generate_names", fake_generate, raising=False)

    result = runpy.run_module("generate_names", run_name="__main__")
    assert "__name__" in result and result["__name__"] == "__main__"

    captured = capsys.readouterr()
    lines = [line for line in captured.out.strip().splitlines() if line]
    assert len(lines) == 50
    assert lines[0] == "namn-0"
    assert calls["count"] == 50
