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
