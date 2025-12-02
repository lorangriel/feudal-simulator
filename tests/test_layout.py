import pytest
import tkinter as tk
from tkinter import font as tkfont

from constants import STATUS_DEFAULT_LINE_COUNT
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
    desired_height, min_height = simulator._calculate_status_heights()

    assert simulator.status_text.cget("height") == STATUS_DEFAULT_LINE_COUNT
    assert desired_height >= line_height * STATUS_DEFAULT_LINE_COUNT
    assert min_height < desired_height


def test_status_text_height_after_resize(simulator, tk_root):
    simulator.root.update_idletasks()
    status_font = tkfont.Font(font=simulator.status_text.cget("font"))
    line_height = max(status_font.metrics("linespace"), 1)
    desired_height, _ = simulator._calculate_status_heights()

    tk_root.geometry("900x700")
    simulator.root.update_idletasks()
    base_height = simulator.status_frame.winfo_height()

    tk_root.geometry("1600x1200")
    simulator.root.update_idletasks()
    larger_height = simulator.status_frame.winfo_height()

    tk_root.geometry("1024x768")
    simulator.root.update_idletasks()
    restored_height = simulator.status_frame.winfo_height()

    assert base_height <= desired_height + line_height
    assert larger_height <= desired_height + line_height
    assert restored_height <= desired_height + line_height
    assert abs(larger_height - base_height) <= line_height


def test_status_desired_height_targets_four_lines(simulator):
    simulator.root.update_idletasks()
    status_font = tkfont.Font(font=simulator.status_text.cget("font"))
    desired_height, min_height = simulator._calculate_status_heights()
    line_height = max(status_font.metrics("linespace"), 1)

    assert line_height * STATUS_DEFAULT_LINE_COUNT <= desired_height <= line_height * (STATUS_DEFAULT_LINE_COUNT + 1)
    assert min_height < desired_height


def test_status_height_logging(tk_root, capsys):
    _ = FeodalSimulator(tk_root)
    output = capsys.readouterr().out

    assert f"{STATUS_DEFAULT_LINE_COUNT} rader" in output


def test_treeview_pack_configuration(simulator):
    pack_info = simulator.tree.pack_info()
    assert pack_info["side"] == tk.LEFT
    assert pack_info["fill"] == tk.BOTH
    assert pack_info["expand"] == "1"


def test_main_paned_children_intact(simulator):
    panes = simulator.paned_window.panes()
    assert len(panes) == 2
    assert panes[1] == str(simulator.right_frame)
