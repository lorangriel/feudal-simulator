import random
from name_randomizer import NameRandomizer


def test_random_name_components():
    random.seed(0)
    rand = NameRandomizer()
    name = rand.random_name()
    assert any(name.lower().startswith(p) for p in rand.name_beg)
    assert any(name.lower().endswith(s) for s in rand.name_end)
    assert name[0].isupper()
