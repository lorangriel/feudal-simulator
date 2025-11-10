"""Random name generation utilities following Drunok conventions."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Set, Tuple

VOWELS = set("aeiouy")
INVALID_STARTS = {"ng", "pt", "ps"}
INVALID_ENDS = {"q", "x", "z"}


def _levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein distance between two strings."""

    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    previous_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current_row = [i]
        for j, cb in enumerate(b, start=1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (ca != cb)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def _contains_vowel(value: str) -> bool:
    return any(ch in VOWELS for ch in value)


def _has_tripled_letters(value: str) -> bool:
    return bool(re.search(r"([a-z])\1\1", value))


def _has_disallowed_triple_consonant(value: str, allowed: Set[str]) -> bool:
    for i in range(len(value) - 2):
        chunk = value[i : i + 3]
        if all(ch not in VOWELS for ch in chunk) and chunk not in allowed:
            return True
    return False


def _clean_name(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower())


def _first_token(name: str) -> str:
    return name.strip().split()[0] if name and name.strip() else ""


def _shares_morpheme(candidate: str, prefixes: Sequence[str], suffixes: Sequence[str], last_vowel: Optional[str]) -> bool:
    cand_lower = candidate.lower()
    for prefix in prefixes:
        if prefix and cand_lower.startswith(prefix):
            return True
    for suffix in suffixes:
        if suffix and cand_lower.endswith(suffix):
            return True
    if last_vowel and cand_lower.endswith(last_vowel):
        return True
    return False


def _distance_ok(candidate: str, reference: str) -> bool:
    return _levenshtein(candidate.lower(), reference.lower()) >= 2


@dataclass(frozen=True)
class LiegeProfile:
    first_name: str
    lower: str
    prefixes: Tuple[str, ...]
    suffixes: Tuple[str, ...]
    last_vowel: Optional[str]


class NameRandomizer:
    """Generates random names based on Drunok culture rules."""

    male_examples: Sequence[str] = (
        "Akala",
        "Anin",
        "Aros",
        "Chelem",
        "Dor",
        "Gahallan",
        "Milcas",
        "Garon",
        "Halvam",
        "Igos",
        "Mael",
        "Menon",
        "Mikal",
        "Naro",
        "Palan",
        "Pavane",
        "Rehelm",
        "Stagus",
        "Tolrune",
        "Valentin",
        "Vite",
    )

    female_examples: Sequence[str] = (
        "Anna",
        "Desira",
        "Drusa",
        "Dolis",
        "Enis",
        "Efa",
        "Gynes",
        "Gun",
        "Ineva",
        "Ivlis",
        "Lenae",
        "Mianni",
        "Nina",
        "Patera",
        "Po",
        "Sabel",
        "Sala",
        "Selima",
        "Sara",
        "Vanis",
        "Villeni",
        "Ygea",
    )

    male_prefixes: Sequence[str] = (
        "ak",
        "an",
        "ar",
        "chel",
        "dor",
        "gah",
        "mil",
        "gar",
        "hal",
        "ig",
        "ma",
        "men",
        "mik",
        "nar",
        "pal",
        "pav",
        "reh",
        "stag",
        "tol",
        "val",
        "vi",
    )

    male_suffixes: Sequence[str] = (
        "ala",
        "in",
        "os",
        "lem",
        "or",
        "allan",
        "cas",
        "on",
        "vam",
        "el",
        "enon",
        "kal",
        "aro",
        "lan",
        "vane",
        "helm",
        "gus",
        "rune",
        "entin",
        "ite",
    )

    male_cores: Sequence[str] = (
        "a",
        "e",
        "i",
        "o",
        "u",
        "al",
        "or",
        "en",
        "ar",
        "rin",
        "hal",
        "dor",
        "van",
        "len",
    )

    female_prefixes: Sequence[str] = (
        "an",
        "des",
        "dru",
        "dol",
        "en",
        "ef",
        "gy",
        "gu",
        "in",
        "iv",
        "len",
        "mian",
        "nin",
        "pat",
        "po",
        "sab",
        "sal",
        "sel",
        "sar",
        "van",
        "vil",
        "yg",
    )

    female_suffixes: Sequence[str] = (
        "na",
        "ira",
        "rusa",
        "olis",
        "nis",
        "fa",
        "ynes",
        "un",
        "eva",
        "lis",
        "ae",
        "anni",
        "tera",
        "o",
        "bel",
        "la",
        "lima",
        "ra",
        "leni",
        "gea",
    )

    female_cores: Sequence[str] = (
        "a",
        "e",
        "i",
        "o",
        "u",
        "an",
        "el",
        "in",
        "or",
        "al",
        "ia",
        "li",
        "na",
        "ra",
    )

    def __init__(self, rng: Optional[random.Random] = None, seed: Optional[int] = None):
        if rng is not None and seed is not None:
            raise ValueError("Provide either rng or seed, not both")
        if rng is not None:
            self._rng = rng
        else:
            self._rng = random.Random(seed)

        self._male_triplets = self._collect_allowed_triplets(self.male_examples)
        self._female_triplets = self._collect_allowed_triplets(self.female_examples)

    def _collect_allowed_triplets(self, examples: Sequence[str]) -> Set[str]:
        allowed: Set[str] = set()
        for name in examples:
            cleaned = _clean_name(name)
            for i in range(len(cleaned) - 2):
                chunk = cleaned[i : i + 3]
                if all(ch not in VOWELS for ch in chunk):
                    allowed.add(chunk)
        return allowed

    def _rng_instance(self, rng_seed: Optional[int]) -> random.Random:
        if rng_seed is not None:
            return random.Random(rng_seed)
        return self._rng

    def _liege_profile(self, liege_name: Optional[str]) -> Optional[LiegeProfile]:
        if not liege_name:
            return None
        first = _first_token(liege_name)
        if not first:
            return None
        lower = _clean_name(first)
        if not lower:
            return None

        prefixes = tuple({lower[:3], lower[:2]})
        suffixes = tuple({lower[-3:], lower[-2:]})
        last_vowel = None
        for ch in reversed(lower):
            if ch in VOWELS:
                last_vowel = ch
                break
        return LiegeProfile(first_name=first.capitalize(), lower=lower, prefixes=prefixes, suffixes=suffixes, last_vowel=last_vowel)

    def _example_pool(self, gender: str) -> Sequence[str]:
        if gender == "F":
            return self.female_examples
        return self.male_examples

    def _building_blocks(self, gender: str) -> Tuple[Sequence[str], Sequence[str], Sequence[str]]:
        if gender == "F":
            return self.female_prefixes, self.female_cores, self.female_suffixes
        return self.male_prefixes, self.male_cores, self.male_suffixes

    def _allowed_triplets(self, gender: str) -> Set[str]:
        if gender == "F":
            return self._female_triplets
        return self._male_triplets

    def _generate_first_name(
        self,
        rng: random.Random,
        gender: str,
        two_morpheme_rate: float,
        liege: Optional[LiegeProfile],
        role: str,
        required_share: bool,
    ) -> str:
        prefixes, cores, suffixes = self._building_blocks(gender)
        examples = tuple(name.lower() for name in self._example_pool(gender))
        allowed_triplets = self._allowed_triplets(gender)

        attempts = 0
        min_len, max_len = 4, 9

        while True:
            attempts += 1
            if attempts > 50:
                max_len = 10
            if attempts > 200:
                raise RuntimeError("Unable to generate a valid name")

            use_two_morpheme = rng.random() < two_morpheme_rate
            candidate = self._compose_name(rng, prefixes, cores, suffixes, use_two_morpheme)

            if not (min_len <= len(candidate) <= max_len):
                continue
            candidate_lower = candidate.lower()
            if candidate_lower in examples:
                continue
            if any(_levenshtein(candidate_lower, example) < 2 for example in examples):
                continue
            if not _contains_vowel(candidate_lower):
                continue
            if _has_tripled_letters(candidate_lower):
                continue
            if _has_disallowed_triple_consonant(candidate_lower, allowed_triplets):
                continue
            if any(candidate_lower.startswith(bad) for bad in INVALID_STARTS):
                continue
            if candidate_lower[-1] in INVALID_ENDS:
                continue
            if liege and not _distance_ok(candidate, liege.first_name):
                continue
            if liege and role != "generic":
                shares = _shares_morpheme(candidate, liege.prefixes, liege.suffixes, liege.last_vowel)
                if required_share and not shares:
                    continue
                return candidate
            return candidate

    def _compose_name(
        self,
        rng: random.Random,
        prefixes: Sequence[str],
        cores: Sequence[str],
        suffixes: Sequence[str],
        use_two_morpheme: bool,
    ) -> str:
        prefix = rng.choice(prefixes)
        core = rng.choice(cores)
        suffix = rng.choice(suffixes)
        name = prefix + core + suffix
        if use_two_morpheme:
            prefix2 = rng.choice(prefixes)
            suffix2 = rng.choice(suffixes)
            bridge = rng.choice(("", "a", "e", "o"))
            name = prefix + core + bridge + prefix2 + suffix2
        return name.capitalize()

    def _generate_surname(
        self,
        rng: random.Random,
        role: str,
        liege: Optional[LiegeProfile],
        genitive_rate: float,
        two_morpheme_rate: float,
    ) -> str:
        if role == "spouse" and liege is not None:
            base = liege.first_name
        else:
            if role in {"child", "relative"} and liege is not None:
                base = liege.first_name
            else:
                base = self._generate_first_name(
                    rng,
                    "M",
                    two_morpheme_rate * 0.5,
                    None,
                    "generic",
                    False,
                )

        if base and rng.random() < genitive_rate and not base.lower().endswith("s"):
            base = base + "s"
        return base

    def _resolve_gender(self, gender: str, role: str, liege: Optional[LiegeProfile], rng: random.Random) -> str:
        gender = gender.upper()
        if gender in {"M", "F"}:
            return gender
        if role == "spouse" and liege is not None:
            male_names = {name.lower() for name in self.male_examples}
            female_names = {name.lower() for name in self.female_examples}
            liege_lower = liege.first_name.lower()
            if liege_lower in male_names:
                return "F"
            if liege_lower in female_names:
                return "M"
            return "F"
        return "M" if rng.random() < 0.5 else "F"

    def generate_names(
        self,
        *,
        gender: str = "AUTO",
        role: str = "generic",
        liege_name: Optional[str] = None,
        count: int = 1,
        uniqueset: Optional[Iterable[str]] = None,
        genitive_rate: float = 0.2,
        two_morpheme_rate: float = 0.15,
        rng_seed: Optional[int] = None,
    ) -> List[str]:
        if count <= 0:
            return []

        rng = self._rng_instance(rng_seed)
        liege = self._liege_profile(liege_name)
        if role != "generic" and liege is None:
            raise ValueError("liege_name is required when role is not generic")

        used: Set[str] = set(uniqueset or [])
        results: List[str] = []

        share_quota: Optional[int] = None
        if liege and role in {"child", "spouse", "relative"}:
            if role == "child":
                ratio = rng.uniform(0.6, 0.8)
            elif role == "relative":
                ratio = rng.uniform(0.4, 0.6)
            else:  # spouse
                ratio = 0.5
            share_quota = max(1, round(count * ratio)) if count > 0 else 0

        for _ in range(count):
            for _ in range(500):
                resolved_gender = self._resolve_gender(gender, role, liege, rng)
                required_share = False
                if share_quota is not None:
                    remaining_slots = count - len(results)
                    required_remaining = max(0, share_quota)
                    if remaining_slots <= 0:
                        required_share = False
                    elif required_remaining >= remaining_slots:
                        required_share = True
                    else:
                        required_share = rng.random() < (required_remaining / remaining_slots)

                first_name = self._generate_first_name(
                    rng,
                    resolved_gender,
                    two_morpheme_rate,
                    liege,
                    role,
                    required_share,
                )
                surname = self._generate_surname(rng, role, liege, genitive_rate, two_morpheme_rate)
                full_name = f"{first_name} {surname}".strip()
                if full_name in used:
                    continue
                used.add(full_name)
                if share_quota is not None and liege:
                    if _shares_morpheme(first_name, liege.prefixes, liege.suffixes, liege.last_vowel):
                        share_quota = max(0, share_quota - 1)
                results.append(full_name)
                break
            else:
                raise RuntimeError("Unable to generate unique names")

        return results

    def random_name(self) -> str:
        """Return a single generic NPC name."""

        return self.generate_names()[0]
