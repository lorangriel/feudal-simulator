"""Standalone script to print a list of random names."""

from __future__ import annotations

from name_randomizer import NameRandomizer


def main(count: int = 50, seed: int | None = None) -> None:
    """Print ``count`` generated names to stdout."""

    randomizer = NameRandomizer(seed=seed)
    for name in randomizer.generate_names(count=count):
        print(name)


if __name__ == "__main__":
    main()
