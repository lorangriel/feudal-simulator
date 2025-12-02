import tkinter as tk
from tkinter import ttk

import pytest

from safe_combobox import SafeCombobox, apply_safe_combobox_patch


@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter root cannot be created in this environment")
    apply_safe_combobox_patch()
    root.withdraw()
    yield root
    root.destroy()


def open_dropdown(combo: SafeCombobox, root: tk.Tk) -> None:
    combo._on_dropdown_open()
    root.update_idletasks()


def test_no_wheel_change_when_closed(tk_root):
    bubbled = []
    tk_root.bind_all("<MouseWheel>", lambda _e: bubbled.append("wheel"), add="+")

    combo = ttk.Combobox(tk_root, values=["A", "B", "C"])
    combo.current(0)
    combo.pack()
    tk_root.update_idletasks()

    combo.event_generate("<MouseWheel>", delta=-120)
    tk_root.update_idletasks()

    assert combo.get() == "A"
    assert bubbled, "MouseWheel should bubble to container when dropdown is closed"


def test_wheel_navigates_when_open(tk_root):
    combo = ttk.Combobox(tk_root, values=["A", "B", "C"])
    combo.current(0)
    combo.pack()
    open_dropdown(combo, tk_root)

    combo.event_generate("<MouseWheel>", delta=-120)
    tk_root.update_idletasks()

    assert combo.get() == "A"
    assert combo.pending_value == "B"
    assert combo.is_dropdown_open()


def test_commit_on_click_simulation(tk_root):
    combo = ttk.Combobox(tk_root, values=["A", "B", "C"])
    combo.current(0)
    combo.pack()
    open_dropdown(combo, tk_root)

    committed = []
    combo.bind("<<ComboboxSelected>>", lambda _e: committed.append(combo.get()), add="+")

    combo.event_generate("<MouseWheel>", delta=-120)
    tk_root.update_idletasks()
    combo._commit_pending_selection("click")
    tk_root.update_idletasks()

    assert combo.get() == "B"
    assert committed == ["B"]


def test_commit_on_close_with_selection(tk_root):
    combo = ttk.Combobox(tk_root, values=["A", "B", "C"])
    combo.current(0)
    combo.pack()
    open_dropdown(combo, tk_root)

    committed = []
    combo.bind("<<ComboboxSelected>>", lambda _e: committed.append(combo.get()), add="+")

    combo.event_generate("<MouseWheel>", delta=-120)
    tk_root.update_idletasks()
    combo._on_dropdown_close()
    tk_root.update_idletasks()

    assert combo.get() == "B"
    assert committed == ["B"]


def test_abort_on_escape(tk_root):
    combo = ttk.Combobox(tk_root, values=["A", "B", "C"])
    combo.current(1)
    combo.pack()
    open_dropdown(combo, tk_root)

    committed = []
    combo.bind("<<ComboboxSelected>>", lambda _e: committed.append(combo.get()), add="+")

    combo.event_generate("<MouseWheel>", delta=-120)
    tk_root.update_idletasks()
    combo._on_escape(None)
    combo._on_dropdown_close()
    tk_root.update_idletasks()

    assert combo.get() == "B"
    assert not committed


def test_global_applicability_for_new_instances(tk_root):
    combo = ttk.Combobox(tk_root, values=["A", "B"])
    assert isinstance(combo, SafeCombobox)

    combo.current(0)
    open_dropdown(combo, tk_root)
    combo.event_generate("<MouseWheel>", delta=-120)
    tk_root.update_idletasks()
    combo._on_dropdown_close()

    assert combo.get() == "B"
