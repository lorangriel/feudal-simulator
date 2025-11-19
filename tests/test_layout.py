import pytest
import tkinter as tk

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
