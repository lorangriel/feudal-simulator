"""Standalone script to print a list of random names."""

from name_randomizer import NameRandomizer


def main() -> None:
    randomizer = NameRandomizer()
    for _ in range(50):
        print(randomizer.random_name())


if __name__ == "__main__":
    main()
