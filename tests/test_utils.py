import random
from src import utils


def test_roll_dice_basic_deterministic():
    random.seed(0)
    value, dbg = utils.roll_dice("3d6")
    assert value == 9
    assert dbg == ""


def test_roll_dice_constant_only():
    random.seed(0)
    value, _ = utils.roll_dice("+5")
    assert value == 5


def test_roll_dice_unlimited_exploding(monkeypatch):
    seq = [6, 6, 2, 3]
    iterator = iter(seq)

    def fake_randint(a, b):
        try:
            return next(iterator)
        except StopIteration:
            return 1

    monkeypatch.setattr(random, "randint", fake_randint)
    value, dbg = utils.roll_dice("ob1d6", debug=True)
    assert value == 6
    assert "6->+2 nya" in dbg


def test_generate_swedish_village_name_components():
    random.seed(0)
    name = utils.generate_swedish_village_name()
    prefixes = [
        "Björk", "Gran", "Lind", "Sjö", "Berg", "Älv", "Hav", "Hög", "Löv", "Ek",
        "Sten", "Sol", "Vind", "Ask", "Rönn", "Klipp", "Dal", "Sand", "Ler", "Moss",
        "Olof", "Erik", "Karl", "Ingrid", "Tor", "Frej", "Ulf", "Sig", "Arne", "Hilda",
        "Sven", "Astrid", "Björn", "Helga", "Sten", "Siv", "Ragnar", "Estrid", "Håkan",
        "Gunnar", "Liv", "Gertrud", "Bo", "Stig", "Svea", "Axel", "Alma",
    ]
    suffixes = [
        "by", "torp", "hult", "ås", "rud", "forsa", "vik", "näs", "tuna", "stad",
        "holm", "änge", "gård", "hed", "dal", "strand", "lid", "sjö", "träsk", "mark",
        "hem", "lösa", "köping", "berga", "lunda", "måla", "ryd", "rum", "sta", "landa",
    ]
    assert any(name.startswith(p) for p in prefixes)
    assert any(name.endswith(s) for s in suffixes)
