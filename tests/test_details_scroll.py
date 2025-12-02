import tkinter as tk
from tkinter import ttk

import pytest

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
    sim.root.update_idletasks()
    return sim


def build_scrollable_details(simulator, item_count=50, include_inner_text=False):
    simulator._clear_right_frame()
    scroll_frame = simulator.create_details_scrollable_frame(padding="0 0 0 0")
    scroll_frame.canvas.config(height=200, width=250)
    scroll_frame.pack(fill="both", expand=True)

    target_label = None
    for idx in range(item_count):
        lbl = ttk.Label(scroll_frame.content, text=f"Rad {idx}")
        lbl.pack()
        target_label = lbl

    text_widget = None
    if include_inner_text:
        text_widget = tk.Text(scroll_frame.content, height=3, width=20)
        for _ in range(20):
            text_widget.insert("end", "Inre scrollrad\n")
        text_widget.pack()

    simulator.root.update_idletasks()
    return scroll_frame, target_label, text_widget


def test_mousewheel_scrolls_details_from_child(simulator):
    scroll_frame, target_label, _ = build_scrollable_details(simulator)
    start = scroll_frame.canvas.yview()

    target_label.event_generate("<MouseWheel>", delta=-120)
    simulator.root.update_idletasks()
    end = scroll_frame.canvas.yview()

    assert end[0] > start[0]


def test_linux_button_events_scroll_details(simulator):
    scroll_frame, target_label, _ = build_scrollable_details(simulator)
    start = scroll_frame.canvas.yview()

    target_label.event_generate("<Button-5>")  # Scroll down
    simulator.root.update_idletasks()
    mid = scroll_frame.canvas.yview()

    target_label.event_generate("<Button-4>")  # Scroll back up
    simulator.root.update_idletasks()
    end = scroll_frame.canvas.yview()

    assert mid[0] > start[0]
    assert end[0] < mid[0]


def test_scrollbar_still_scrolls_with_mousewheel(simulator):
    scroll_frame, _target_label, _ = build_scrollable_details(simulator)
    start = scroll_frame.canvas.yview()

    scroll_frame.vscroll.event_generate("<MouseWheel>", delta=-120)
    simulator.root.update_idletasks()
    end = scroll_frame.canvas.yview()

    assert end[0] > start[0]


def test_inner_scroll_widget_takes_priority(simulator):
    scroll_frame, _target_label, text_widget = build_scrollable_details(
        simulator, include_inner_text=True
    )
    start_details = scroll_frame.canvas.yview()
    start_inner = text_widget.yview()

    text_widget.event_generate("<MouseWheel>", delta=-120)
    simulator.root.update_idletasks()
    end_details = scroll_frame.canvas.yview()
    end_inner = text_widget.yview()

    assert end_inner[0] > start_inner[0]
    assert end_details[0] == pytest.approx(start_details[0])


def test_scroll_binding_survives_rebuild(simulator):
    _ = build_scrollable_details(simulator)
    scroll_frame, target_label, _ = build_scrollable_details(simulator)
    start = scroll_frame.canvas.yview()

    target_label.event_generate("<MouseWheel>", delta=-120)
    simulator.root.update_idletasks()
    end = scroll_frame.canvas.yview()

    assert end[0] > start[0]


def test_other_panels_do_not_scroll_details(simulator):
    scroll_frame, _target_label, _ = build_scrollable_details(simulator)
    start = scroll_frame.canvas.yview()

    simulator.tree.event_generate("<MouseWheel>", delta=-120)
    simulator.root.update_idletasks()
    end = scroll_frame.canvas.yview()

    assert end[0] == pytest.approx(start[0])


def test_mousewheel_noop_when_not_scrollable(simulator):
    scroll_frame, target_label, _ = build_scrollable_details(simulator, item_count=2)
    start = scroll_frame.canvas.yview()

    target_label.event_generate("<MouseWheel>", delta=-120)
    simulator.root.update_idletasks()
    end = scroll_frame.canvas.yview()

    assert end[0] == pytest.approx(start[0])
