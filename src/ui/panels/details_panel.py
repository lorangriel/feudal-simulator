"""Panelklass för Detaljer."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.strings import format_details_title, panel_tooltip


class DetailsPanel:
    """Wrapper runt detaljer-panelens header och body."""

    def __init__(self, parent: tk.Misc, tooltip_manager):
        self.header = ttk.Label(
            parent,
            text=format_details_title(None),
            font=("Arial", 14, "bold"),
            anchor="w",
            padding=(10, 6),
        )
        self.header.pack(fill="x", padx=2, pady=(2, 0))
        tooltip_manager.set_tooltip(self.header, panel_tooltip("details"))

        self.body = ttk.Frame(parent, style="Content.TFrame")
        self.body.pack(fill="both", expand=True)

    def update_title(self, resource_name: str | None) -> None:
        try:
            self.header.config(text=format_details_title(resource_name))
        except tk.TclError:
            return
