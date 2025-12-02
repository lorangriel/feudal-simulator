"""Panelklass för Status."""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from constants import STATUS_DEFAULT_LINE_COUNT
from ui.strings import PANEL_NAMES, panel_tooltip


class StatusPanel:
    """Visar sammanfattande status och hanterar default-höjd."""

    def __init__(self, parent: tk.Misc, tooltip_manager):
        self.frame = ttk.LabelFrame(parent, text=PANEL_NAMES["status"], padding=5)
        self.text = tk.Text(
            self.frame,
            height=STATUS_DEFAULT_LINE_COUNT,
            wrap="word",
            state="disabled",
            relief=tk.FLAT,
            bg="#f0f0f0",
            font=("Arial", 9),
        )
        status_scroll = ttk.Scrollbar(self.frame, command=self.text.yview)
        self.text.config(yscrollcommand=status_scroll.set)
        status_scroll.pack(side=tk.RIGHT, fill="y")
        self.text.pack(side=tk.LEFT, fill="both", expand=True)
        tooltip_manager.set_tooltip(self.frame, panel_tooltip("status"))

    # ------------------------------------------------------------------
    # Höjdberäkningar
    # ------------------------------------------------------------------
    def calculate_heights(self) -> tuple[int, int]:
        try:
            status_font = tkfont.Font(font=self.text.cget("font"))
            line_height = status_font.metrics("linespace")
            if line_height <= 0:
                line_height = 16
            self.text.update_idletasks()
            text_req_height = max(self.text.winfo_reqheight(), line_height)
            frame_req_height = max(self.frame.winfo_reqheight(), text_req_height)
            chrome_height = max(
                text_req_height - line_height * STATUS_DEFAULT_LINE_COUNT, 0
            )
            frame_overhead = max(frame_req_height - text_req_height, 0)
            desired_height = frame_overhead + text_req_height
            min_height = frame_overhead + chrome_height + line_height
            return max(desired_height, 0), max(min_height, 1)
        except tk.TclError:
            chrome_height = 8
            desired_height = line_height * STATUS_DEFAULT_LINE_COUNT + chrome_height
            min_height = line_height + chrome_height
            return desired_height, min_height
