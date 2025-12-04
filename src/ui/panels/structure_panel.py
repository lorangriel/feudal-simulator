"""Panelklass för Struktur."""
from __future__ import annotations

import tkinter as tk
import warnings
from tkinter import ttk

from ui.strings import PANEL_NAMES, STRUCTURE_ACTIONS, panel_tooltip


class StructurePanel:
    """Innehåller trädet och dess scrollbars."""

    def __init__(self, parent: tk.Misc, tooltip_manager, on_double_click):
        self.mode = "admin"
        self.tooltip_manager = tooltip_manager
        self.default_tree_tooltip = panel_tooltip("structure")
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
        self.show_personal_button = None  # Deprecated, button moved to details panel
        self.back_button = ttk.Button(
            self.button_frame,
            text=STRUCTURE_ACTIONS["back"],
            command=self._on_back,
        )
        self.back_button.pack(side=tk.LEFT)
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
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)
        tooltip_manager.set_tooltip(self.tree, self.default_tree_tooltip)

        self._back_command = None
        self.personal_icon = "◆"

    def _on_back(self):
        if self._back_command:
            self._back_command()

    def set_show_personal_command(self, _callback):
        warnings.warn(
            "set_show_personal_command is deprecated; personal province button now lives in the details panel.",
            DeprecationWarning,
            stacklevel=2,
        )

    def set_back_command(self, callback):
        self._back_command = callback

    def format_node_label(self, base_text: str, is_personal: bool) -> str:
        if is_personal:
            return f"{self.personal_icon} {base_text}"
        return base_text

    def update_mode(self, mode: str) -> None:
        self.mode = mode
        if mode == "province":
            self.tree.heading("#0", text=STRUCTURE_ACTIONS["province_view"])
            self.back_button.pack(side=tk.LEFT)
        else:
            self.tree.heading("#0", text=PANEL_NAMES["structure"])
            self.back_button.pack_forget()
        self._reset_tree_tooltip()

    def show_personal_toggle(self, should_show: bool) -> None:
        warnings.warn(
            "show_personal_toggle is deprecated; personal province button now lives in the details panel.",
            DeprecationWarning,
            stacklevel=2,
        )

    def _on_tree_motion(self, event):
        if self.mode != "admin":
            self._reset_tree_tooltip()
            return

        item_id = self.tree.identify_row(event.y)
        is_personal = bool(
            item_id and "personal_province" in self.tree.item(item_id, "tags")
        )

        if is_personal:
            if self.tooltip_manager._tooltips.get(self.tree) != "Personlig provins":
                self.tooltip_manager._tooltips[self.tree] = "Personlig provins"
                self.tooltip_manager._hide()
                self.tooltip_manager._maybe_show(self.tree)
        else:
            self._reset_tree_tooltip()

    def _on_tree_leave(self, _event):
        self._reset_tree_tooltip()
        self.tooltip_manager._hide()

    def _reset_tree_tooltip(self) -> None:
        current = self.tooltip_manager._tooltips.get(self.tree)
        if current != self.default_tree_tooltip:
            self.tooltip_manager._tooltips[self.tree] = self.default_tree_tooltip
