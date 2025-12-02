"""Tooltip-hjälpare för UI."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class TooltipManager:
    """Lightweight tooltip helper that also tracks missing texts."""

    def __init__(self, root: tk.Misc):
        self.root = root
        self._tooltips: dict[tk.Misc, str] = {}
        self._tipwindow: tk.Toplevel | None = None

    def set_tooltip(self, widget: tk.Misc, text: str | None) -> None:
        """Attach ``text`` to ``widget``. Empty text marks the widget as missing."""

        self._tooltips[widget] = (text or "").strip()
        widget.bind("<Enter>", lambda event, w=widget: self._maybe_show(w))
        widget.bind("<Leave>", lambda _event: self._hide())
        widget.bind("<FocusOut>", lambda _event: self._hide())

    def _maybe_show(self, widget: tk.Misc) -> None:
        text = self._tooltips.get(widget)
        if not text:
            return
        self._hide()
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + widget.winfo_height() + 5
        try:
            self._tipwindow = tw = tk.Toplevel(widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(
                tw,
                text=text,
                background="#fdf8d8",
                relief=tk.SOLID,
                borderwidth=1,
                justify=tk.LEFT,
                font=("Arial", 9),
                padx=6,
                pady=3,
            )
            label.pack(ipadx=1)
        except tk.TclError:
            self._tipwindow = None

    def _hide(self) -> None:
        if self._tipwindow is not None:
            try:
                self._tipwindow.destroy()
            except tk.TclError:
                pass
        self._tipwindow = None

    def _grid_label_for_widget(self, widget: tk.Misc) -> str:
        """Best-effort lookup for a label in the same grid row."""

        try:
            info = widget.grid_info()
        except tk.TclError:
            return ""
        parent = widget.nametowidget(widget.winfo_parent())
        if not hasattr(parent, "grid_slaves"):
            return ""
        try:
            row = int(info.get("row", -1))
            column = int(info.get("column", 0))
        except (TypeError, ValueError):
            return ""
        if row < 0:
            return ""
        for candidate in parent.grid_slaves(row=row):
            if int(candidate.grid_info().get("column", -1)) == column - 1:
                if isinstance(candidate, (tk.Label, ttk.Label)):
                    try:
                        return str(candidate.cget("text"))
                    except tk.TclError:
                        return ""
        return ""

    def find_missing_tooltips(self) -> list[dict[str, str]]:
        """Return metadata for widgets missing tooltip text."""

        targets: tuple[type, ...] = (
            tk.Entry,
            ttk.Entry,
            ttk.Combobox,
            ttk.Checkbutton,
            ttk.Radiobutton,
            ttk.Button,
        )
        missing: list[dict[str, str]] = []

        def walk(widget: tk.Misc) -> None:
            try:
                children = widget.winfo_children()
            except tk.TclError:
                return
            for child in children:
                if isinstance(child, targets):
                    text = self._tooltips.get(child, "")
                    if not text:
                        toplevel = child.winfo_toplevel()
                        form_name = getattr(toplevel, "title", lambda: "")()
                        if not form_name:
                            form_name = toplevel.__class__.__name__
                        missing.append(
                            {
                                "form": form_name,
                                "widget": child.winfo_name(),
                                "label": self._grid_label_for_widget(child),
                                "type": child.__class__.__name__,
                            }
                        )
                walk(child)

        walk(self.root)
        return missing
