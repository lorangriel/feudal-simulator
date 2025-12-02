"""Panelklass för Struktur."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.strings import PANEL_NAMES, panel_tooltip


class StructurePanel:
    """Innehåller trädet och dess scrollbars."""

    def __init__(self, parent: tk.Misc, tooltip_manager, on_double_click):
        self.frame = ttk.Frame(
            parent, width=350, relief=tk.SUNKEN, borderwidth=1, padding=5
        )
        self.frame.pack(fill="both", expand=True)

        self.header = ttk.Label(
            self.frame,
            text=PANEL_NAMES["structure"],
            font=("Arial", 12, "bold"),
            anchor="w",
            padding=(4, 2),
        )
        self.header.pack(fill="x", pady=(0, 2))
        tooltip_manager.set_tooltip(self.header, panel_tooltip("structure"))

        content = ttk.Frame(self.frame)
        content.pack(fill="both", expand=True)

        tree_vscroll = ttk.Scrollbar(content, orient="vertical")
        tree_hscroll = ttk.Scrollbar(content, orient="horizontal")

        self.tree = ttk.Treeview(
            content,
            yscrollcommand=tree_vscroll.set,
            xscrollcommand=tree_hscroll.set,
            selectmode="browse",
            padding=(6, 6),
        )
        tree_vscroll.config(command=self.tree.yview)
        tree_hscroll.config(command=self.tree.xview)
        tree_vscroll.pack(side=tk.RIGHT, fill="y")
        tree_hscroll.pack(side=tk.BOTTOM, fill="x")
        self.tree.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 4), pady=4)

        self.tree["columns"] = ("#0",)
        self.tree.heading("#0", text=PANEL_NAMES["structure"])
        self.tree.column("#0", width=300, minwidth=200, stretch=tk.YES)
        self.tree.bind("<Double-1>", on_double_click)
        tooltip_manager.set_tooltip(self.tree, panel_tooltip("structure"))
