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

        self.ownership_frame = ttk.Frame(parent, padding=(10, 2))
        self.ownership_label = ttk.Label(
            self.ownership_frame, text="Ägande:", font=("Arial", 10, "bold")
        )
        self.ownership_label.pack(side=tk.LEFT, padx=(0, 6))

        self.ownership_var = tk.StringVar()
        self.ownership_combobox = ttk.Combobox(
            self.ownership_frame,
            textvariable=self.ownership_var,
            state="readonly",
            width=40,
            style="BlackWhite.TCombobox",
        )
        self.ownership_combobox.pack(side=tk.LEFT, fill="x", expand=True)
        self.ownership_value_map: dict[str, tuple[str, int | None]] = {}
        self.hide_ownership_controls()

        self.body = ttk.Frame(parent, style="Content.TFrame")
        self.body.pack(fill="both", expand=True)

    def update_title(self, resource_name: str | None) -> None:
        try:
            self.header.config(text=format_details_title(resource_name))
        except tk.TclError:
            return

    def hide_ownership_controls(self) -> None:
        try:
            self.ownership_frame.pack_forget()
        except tk.TclError:
            return

    def show_ownership_controls(self) -> None:
        try:
            if not self.ownership_frame.winfo_manager():
                self.ownership_frame.pack(fill="x", padx=2, pady=(2, 4))
        except tk.TclError:
            return

    def populate_ownership_combobox(self, app, node_id: int, node_data: dict) -> str:
        """Fyll ägande-comboboxen med dynamiska val."""

        default_label = "Lokal ägo (default)"
        options: list[tuple[str, tuple[str, int | None]]] = [
            (default_label, ("none", None))
        ]

        for level, prefix in ((0, "Kungariket"), (1, "Furstendömet"), (2, "Hertigdömet")):
            for owner in app.get_all_owners_by_level(level):
                owner_id = owner.get("node_id")
                if owner_id is None:
                    continue
                owner_name = app.get_display_name(owner_id)
                label = f"{prefix} {owner_name}"
                options.append((label, (str(level), owner_id)))

        self.ownership_value_map = {label: value for label, value in options}
        self.ownership_combobox.config(values=[label for label, _ in options])
        self.show_ownership_controls()

        current_level = str(node_data.get("owner_assigned_level", "none") or "none")
        current_owner = node_data.get("owner_assigned_id")

        selected_label = default_label
        for label, (level, owner_id) in options:
            if level != current_level:
                continue
            if level == "none" or owner_id == current_owner:
                selected_label = label
                break

        self.ownership_var.set(selected_label)
        return selected_label

    def get_ownership_choice(self, label: str) -> tuple[str, int | None] | None:
        """Return mapping for the given label if present."""

        return self.ownership_value_map.get(label)
