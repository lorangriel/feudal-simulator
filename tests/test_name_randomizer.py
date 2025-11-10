from __future__ import annotations

from name_randomizer import NameRandomizer


def split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def shares_with_liege(first_name: str, liege: str) -> bool:
    liege_lower = liege.lower()
    candidate = first_name.lower()
    prefixes = {liege_lower[:2], liege_lower[:3]}
    suffixes = {liege_lower[-2:], liege_lower[-3:]}
    if any(candidate.startswith(p) for p in prefixes if p):
        return True
    if any(candidate.endswith(s) for s in suffixes if s):
        return True
    if liege_lower and candidate.endswith(liege_lower[-1]):
        return True
    return False


def test_generate_generic_names_are_unique():
    randomizer = NameRandomizer(seed=42)
    names = randomizer.generate_names(count=10)
    assert len(names) == 10
    assert len(set(names)) == 10
    for full_name in names:
        first, surname = split_name(full_name)
        assert first[0].isupper()
        assert surname[0].isupper()
        assert len(first) >= 4


def test_rng_seed_reproducible():
    randomizer = NameRandomizer()
    first_batch = randomizer.generate_names(count=5, rng_seed=1234)
    second_batch = randomizer.generate_names(count=5, rng_seed=1234)
    assert first_batch == second_batch


def test_child_name_matches_liege_profile_and_patronymic():
    randomizer = NameRandomizer(seed=7)
    liege_name = "Tolrune Pavane"
    names = randomizer.generate_names(role="child", liege_name=liege_name, count=5, rng_seed=51)

    liege_first = liege_name.split()[0]
    shares = 0
    for full_name in names:
        first, surname = split_name(full_name)
        assert surname.startswith(liege_first[:])
        if shares_with_liege(first, liege_first):
            shares += 1
    assert shares >= 3


def test_spouse_takes_liege_surname():
    randomizer = NameRandomizer(seed=11)
    liege_name = "Rehelm Tolrune"
    names = randomizer.generate_names(role="spouse", liege_name=liege_name, count=3, rng_seed=22)
    liege_first = liege_name.split()[0]
    for full_name in names:
        first, surname = split_name(full_name)
        assert surname.startswith(liege_first)
        assert first != liege_first


def test_uniqueset_prevents_reuse():
    randomizer = NameRandomizer(seed=15)
    existing = {"Anin Dor"}
    names = randomizer.generate_names(count=3, uniqueset=existing, rng_seed=100)
    assert not any(name in existing for name in names)
