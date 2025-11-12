import random
import tkinter as tk
from tkinter import ttk

import pytest

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
    assert isinstance(name, str)
    assert name == "Hildatorp"


def test_generate_character_name_deterministic():
    random.seed(0)
    male = utils.generate_character_name("m")
    random.seed(0)
    female = utils.generate_character_name("f")
    assert male == "Mate Alen"
    assert female == "Mianeni Alen"


def test_parse_int_10_valid_and_invalid():
    class Bad:
        def __str__(self):
            raise RuntimeError("boom")

    assert utils.parse_int_10("42") == 42
    assert utils.parse_int_10(" 7 ") == 7
    assert utils.parse_int_10(5) == 5
    assert utils.parse_int_10("abc") == 0
    assert utils.parse_int_10("") == 0
    assert utils.parse_int_10(None) == 0
    # Object raising in __str__ should yield 0
    assert utils.parse_int_10(Bad()) == 0


def test_scrollable_frame_adds_scrollbar_when_content_overflows():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()

    try:
        frame = utils.ScrollableFrame(root)
        frame.pack(fill="both", expand=True)
        root.update_idletasks()

        # Initially the scrollbar should stay hidden for small content
        assert not frame.vscroll.winfo_ismapped()

        for _ in range(40):
            ttk.Label(frame.content, text="rad").pack()
        root.update_idletasks()

        assert frame.vscroll.winfo_ismapped()
    finally:
        root.destroy()
