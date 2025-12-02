import tkinter as tk
from tkinter import ttk

import pytest

from src.ui import app as ui_app
from src import simulator


@pytest.fixture
def root():
    try:
        r = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk-display saknas, hoppar över UI-test")
    r.withdraw()
    yield r
    try:
        r.destroy()
    except tk.TclError:
        pass


def test_app_can_be_created(root):
    app = ui_app.create_app(root)
    assert app.root is root
    assert hasattr(app, "structure_panel")
    assert hasattr(app, "status_panel")
    assert hasattr(app, "details_panel")


def test_simulator_shim_points_to_ui_main():
    assert simulator.main is ui_app.main


def test_panel_headers(root):
    app = ui_app.create_app(root)
    assert app.structure_panel.header.cget("text") == "Struktur"
    assert app.status_frame.cget("text") == "Status"
    app.update_details_header("Test")
    assert "Detaljer" in app.details_header.cget("text")


def test_status_height_default_lines(root):
    app = ui_app.create_app(root)
    desired, minimum = app._calculate_status_heights()
    assert desired >= minimum
    # at least four lines worth of height
    assert desired >= app.status_text.cget("height") * 2


def test_combobox_policy_applied(root):
    app = ui_app.create_app(root)
    combo = ttk.Combobox(app.root, values=["a", "b"])
    # ttk.Combobox is patched to SafeCombobox
    from src.safe_combobox import SafeCombobox

    assert isinstance(combo, SafeCombobox)
