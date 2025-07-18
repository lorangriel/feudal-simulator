"""Standalone script to print the character slot display."""

import sys

from slot_display import CharacterSlotDisplay


def main() -> None:
    display = CharacterSlotDisplay()
    sys.stdout.write(display.to_text() + "\n")


if __name__ == "__main__":
    main()
