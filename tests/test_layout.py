import pytest
import tkinter as tk
from tkinter import font as tkfont

from feodal_simulator import FeodalSimulator


@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter root cannot be created in this environment")
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def simulator(tk_root):
    sim = FeodalSimulator(tk_root)
    yield sim


def test_main_vertical_paned_orientation(simulator):
    assert isinstance(simulator.main_vertical_paned, tk.PanedWindow)
    assert simulator.main_vertical_paned.cget("orient") == tk.VERTICAL


def test_status_frame_added_to_vertical_paned(simulator):
    panes = simulator.main_vertical_paned.panes()
    assert str(simulator.main_frame) in panes
    assert str(simulator.status_frame) in panes
    assert simulator.status_text.master is simulator.status_frame


def test_status_text_initial_height(simulator):
    simulator.root.update_idletasks()
    status_font = tkfont.Font(font=simulator.status_text.cget("font"))
    line_height = max(status_font.metrics("linespace"), 1)
    status_height = simulator.status_text.winfo_height()

    min_expected = line_height * 4
    max_expected = line_height * 6
    assert min_expected <= status_height <= max_expected


def test_status_text_height_after_resize(simulator, tk_root):
    simulator.root.update_idletasks()
    status_font = tkfont.Font(font=simulator.status_text.cget("font"))
    line_height = max(status_font.metrics("linespace"), 1)

    tk_root.geometry("900x700")
    simulator.root.update_idletasks()
    base_height = simulator.status_text.winfo_height()

    tk_root.geometry("1600x1200")
    simulator.root.update_idletasks()
    larger_height = simulator.status_text.winfo_height()

    tk_root.geometry("1024x768")
    simulator.root.update_idletasks()
    restored_height = simulator.status_text.winfo_height()

    max_expected = line_height * 6
    assert larger_height <= max_expected
    assert restored_height <= max_expected
    assert abs(larger_height - base_height) <= line_height * 1.5


def test_treeview_pack_configuration(simulator):
    pack_info = simulator.tree.pack_info()
    assert pack_info["side"] == tk.LEFT
    assert pack_info["fill"] == tk.BOTH
    assert pack_info["expand"] == "1"


def test_main_paned_children_intact(simulator):
    panes = simulator.paned_window.panes()
    assert len(panes) == 2
    assert panes[1] == str(simulator.right_frame)
