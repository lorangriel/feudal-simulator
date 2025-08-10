import random
from generate_names import main
from name_randomizer import NameRandomizer


def test_main_prints_deterministic_names(capsys):
    random.seed(0)
    rand = NameRandomizer()
    expected = [rand.random_name() for _ in range(50)]

    random.seed(0)
    main()
    captured = capsys.readouterr()
    output = captured.out.strip().splitlines()
    assert output == expected
    assert len(output) == 50
