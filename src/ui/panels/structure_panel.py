"""Panelklass för Struktur."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.strings import PANEL_NAMES, STRUCTURE_ACTIONS, TOOLTIPS, panel_tooltip


class StructurePanel:
    """Innehåller trädet och dess scrollbars."""

    def __init__(self, parent: tk.Misc, tooltip_manager, on_double_click):
        self.mode = "admin"
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

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill="x", pady=(0, 2))
        self.show_personal_button = ttk.Button(
            self.button_frame,
            text=STRUCTURE_ACTIONS["show_personal"],
            command=self._on_show_personal,
        )
        self.back_button = ttk.Button(
            self.button_frame,
            text=STRUCTURE_ACTIONS["back"],
            command=self._on_back,
        )
        self.show_personal_button.pack(side=tk.LEFT, padx=(0, 4))
        self.back_button.pack(side=tk.LEFT)
        tooltip_manager.set_tooltip(
            self.show_personal_button, TOOLTIPS.get("show_personal")
        )
        self.show_personal_button.pack_forget()
        self.back_button.pack_forget()

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

        self._show_personal_command = None
        self._back_command = None

    def _on_show_personal(self):
        if self._show_personal_command:
            self._show_personal_command()

    def _on_back(self):
        if self._back_command:
            self._back_command()

    def set_show_personal_command(self, callback):
        self._show_personal_command = callback

    def set_back_command(self, callback):
        self._back_command = callback

    def update_mode(self, mode: str) -> None:
        self.mode = mode
        if mode == "province":
            self.tree.heading("#0", text=STRUCTURE_ACTIONS["province_view"])
            self.back_button.pack(side=tk.LEFT)
            self.show_personal_button.pack_forget()
        else:
            self.tree.heading("#0", text=PANEL_NAMES["structure"])
            self.back_button.pack_forget()

    def show_personal_toggle(self, should_show: bool) -> None:
        if should_show and self.mode == "admin":
            if not self.show_personal_button.winfo_manager():
                self.show_personal_button.pack(side=tk.LEFT, padx=(0, 4))
        else:
            self.show_personal_button.pack_forget()
