"""Fristående vy för nod-detaljer och redigering."""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox, ttk

from ui.strings import PANEL_NAMES, format_details_title
from utils import ScrollableFrame


class NodeDetailsView:
    """Ansvarar för rendering och interaktion i detaljpanelen."""

    def __init__(self, app, details_panel, status_service, event_bus):
        self.app = app
        self.details_panel = details_panel
        self.status_service = status_service
        self.event_bus = event_bus

        self.details_header = details_panel.header
        self.details_body = details_panel.body

        self._ownership_target_id: int | None = None
        self._ownership_last_selection: str | None = None
        self._suppress_ownership_callback = False

        self._details_scroll_target: tk.Misc | None = None
        self._details_mousewheel_bound = False
        self._bind_details_mousewheel()

    # --- Logging helpers ---
    def _log_panel_event(self, panel_key: str, action: str) -> None:
        panel_name = PANEL_NAMES.get(panel_key, panel_key)
        print(f"{panel_name}: {action}")

    # --- Scroll/Mousewheel management ---
    def _bind_details_mousewheel(self) -> None:
        if self._details_mousewheel_bound:
            return
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.app.root.bind_all(sequence, self._on_details_mousewheel, add="+")
        self._details_mousewheel_bound = True
        self._log_panel_event(
            "details",
            "Globalt mushjuls-scrollstöd aktiverat (canvas-yview-backing)",
        )

    def _widget_in_details(self, widget: tk.Misc | str | None) -> bool:
        if widget is None or not hasattr(self, "details_body"):
            return False

        try:
            current: tk.Misc | None
            if isinstance(widget, str):
                current = self.app.root.nametowidget(widget)
            else:
                current = widget

            while current is not None:
                if current is self.details_body:
                    return True
                parent_name = current.winfo_parent()
                if not parent_name:
                    break
                current = current.nametowidget(parent_name)
        except (tk.TclError, AttributeError, KeyError):
            return False
        return False

    @staticmethod
    def _normalize_mousewheel_delta(event: tk.Event) -> int:
        event_num = getattr(event, "num", None)
        if event_num in (4, 5):
            return -1 if event_num == 4 else 1

        delta = getattr(event, "delta", 0)
        if delta == 0:
            return 0
        if sys.platform == "darwin":
            return -int(delta)

        step = int(delta / 120) if abs(delta) >= 120 else int(delta / abs(delta))
        return -step

    def _on_details_mousewheel(self, event: tk.Event) -> None:
        pointer_widget = None
        try:
            pointer_widget = self.app.root.winfo_containing(
                self.app.root.winfo_pointerx(), self.app.root.winfo_pointery()
            )
        except (tk.TclError, KeyError):
            pointer_widget = None

        target_widget = event.widget if self._widget_in_details(event.widget) else None
        if target_widget is None and not self._widget_in_details(pointer_widget):
            return

        target = self._details_scroll_target
        if not target or not hasattr(target, "yview_scroll"):
            return
        try:
            if not target.winfo_exists():
                self._details_scroll_target = None
                return
        except tk.TclError:
            self._details_scroll_target = None
            return

        units = self._normalize_mousewheel_delta(event)
        if units == 0:
            return

        try:
            target.yview_scroll(units * self.app.DETAILS_SCROLL_UNITS, "units")
        except tk.TclError:
            self._details_scroll_target = None

    def _set_details_scroll_target(self, widget: tk.Misc | None) -> None:
        self._details_scroll_target = widget
        if widget is not None:
            self._log_panel_event("details", "Scroll-target uppdaterad")

    def create_details_scrollable_frame(
        self, parent: tk.Misc | None = None, *args, **kwargs
    ) -> ScrollableFrame:
        scroll_view = ScrollableFrame(parent or self.details_body, *args, **kwargs)
        self._set_details_scroll_target(scroll_view.canvas)
        return scroll_view

    # --- Header and content lifecycle ---
    def update_details_header(self, resource_name: str | None) -> None:
        if not hasattr(self, "details_header"):
            return
        try:
            self.details_panel.update_title(resource_name)
            title = format_details_title(resource_name)
        except tk.TclError:
            return
        self._log_panel_event("details", f"Uppdaterad till '{title}'")

    def clear(self) -> None:
        if not hasattr(self, "details_body"):
            return

        if self.app.static_map_canvas:
            self.app.static_map_canvas.unbind("<Motion>")
            self.app.static_map_canvas = None

        if self.app.dynamic_map_view:
            try:
                self.app.dynamic_map_view.hide_tooltip()
            except Exception:
                pass
            self.app.dynamic_map_view = None

        self.update_details_header(None)
        self.details_panel.hide_ownership_controls()
        self._set_details_scroll_target(None)
        for widget in self.details_body.winfo_children():
            widget.destroy()

        self.app.map_drag_start_node_id = None
        self.app.map_drag_line_id = None
        self.app.hex_drag_node_id = None
        self.app.hex_drag_start = None

    # --- Ownership handling ---
    def _set_ownership_selection(self, label: str) -> None:
        self._suppress_ownership_callback = True
        try:
            self.details_panel.ownership_var.set(label)
        finally:
            self._suppress_ownership_callback = False

    def update_ownership_controls(self, node_id: int | None, depth: int | None) -> None:
        if not node_id or depth != 3 or not self.app.world_data:
            self._ownership_target_id = None
            self._ownership_last_selection = None
            self.details_panel.hide_ownership_controls()
            return

        node_data = self.app.world_data.get("nodes", {}).get(str(node_id))
        if not node_data:
            self._ownership_target_id = None
            self._ownership_last_selection = None
            self.details_panel.hide_ownership_controls()
            return

        self._ownership_target_id = node_id
        selected_label = self.details_panel.populate_ownership_combobox(
            self.app, node_id, node_data
        )
        self._ownership_last_selection = selected_label
        self._set_ownership_selection(selected_label)

    def on_ownership_selected(self, _event=None):
        if self._suppress_ownership_callback:
            return

        node_id = self._ownership_target_id
        if node_id is None or not self.app.world_data:
            return

        node_data = self.app.world_data.get("nodes", {}).get(str(node_id))
        if not node_data:
            return

        selection_label = self.details_panel.ownership_var.get()
        choice = self.details_panel.get_ownership_choice(selection_label)
        if choice is None:
            return

        candidate_level, candidate_owner_id = choice

        if (
            candidate_level == str(node_data.get("owner_assigned_level", "none"))
            and candidate_owner_id == node_data.get("owner_assigned_id")
        ):
            self._ownership_last_selection = selection_label
            return

        result = self.app.world_manager.assign_personal_owner(
            node_id, (candidate_level, candidate_owner_id)
        )

        if not result.success:
            messagebox.showerror(
                "Ogiltig tilldelning",
                result.message or "Ogiltig tilldelning – ändringen avbröts.",
                parent=self.app.root,
            )
            if self._ownership_last_selection is not None:
                self._set_ownership_selection(self._ownership_last_selection)
            return

        refreshed_node = self.app.world_data.get("nodes", {}).get(
            str(node_id), node_data
        )
        refreshed_label = self.details_panel.populate_ownership_combobox(
            self.app, node_id, refreshed_node
        )
        self._ownership_last_selection = refreshed_label
        self._set_ownership_selection(refreshed_label)

        if not result.changed:
            return

        owner_name = "Lokal ägo"
        if result.owner_id is not None:
            try:
                owner_name = self.app.get_display_name(result.owner_id)
            except Exception:
                owner_name = str(result.owner_id)

        self.status_service.add_message(f"Ägare uppdaterad: {owner_name}")
        if self.event_bus:
            emit_fn = getattr(self.event_bus, "emit", None)
            if callable(emit_fn):
                emit_fn(
                    "ui.owner.changed",
                    node_id=node_id,
                    owner_id=result.owner_id,
                    owner_level=result.owner_level,
                )

    # --- Rendering entrypoints ---
    def show_node_view(self, node_data):
        self.app.commit_pending_changes()
        self.clear()
        self.app.personal_province_button = None

        if not isinstance(node_data, dict):
            self.app.add_status_message(
                f"Fel: Ogiltig noddata mottagen: {node_data}"
            )
            self.app.show_no_world_view()
            return

        node_id = node_data.get("node_id")
        if node_id is None:
            self.app.add_status_message("Fel: Kan inte visa nodvy, noden saknar ID.")
            self.app.show_no_world_view()
            return

        depth = self.app.get_depth_of_node(node_id)
        display_name = self.app.get_display_name_for_node(node_data, depth)
        self.update_details_header(display_name)
        self.update_ownership_controls(node_id, depth)

        view_frame = ttk.Frame(self.details_body, padding="10 10 10 10")
        view_frame.pack(fill="both", expand=True)
        view_frame.grid_rowconfigure(1, weight=1)
        view_frame.grid_columnconfigure(0, weight=1)

        title_frame = ttk.Frame(view_frame)
        title_frame.pack(fill="x", pady=(8, 20))
        title_label = ttk.Label(
            title_frame, text=f"{display_name}", font=("Arial", 18, "bold"), padding=(0, 4)
        )
        title_label.pack(side=tk.LEFT)
        ttk.Label(
            title_frame, text=f" (ID: {node_id}, Djup: {depth})", font=("Arial", 10)
        ).pack(side=tk.LEFT, anchor="s", padx=5)

        scroll_frame = self.create_details_scrollable_frame(view_frame)
        scroll_frame.pack(fill="both", expand=True)
        editor_content_frame = scroll_frame.content

        if depth < 0:
            ttk.Label(
                editor_content_frame,
                text="Fel: Kan inte bestämma nodens position i hierarkin.",
                foreground="red",
            ).pack(pady=10)
        elif depth < 3:
            self.app._show_upper_level_node_editor(editor_content_frame, node_data, depth)
        elif depth == 3:
            self.app._show_jarldome_editor(editor_content_frame, node_data)
        else:
            self.app._show_resource_editor(editor_content_frame, node_data, depth)

        self._log_panel_event("details", f"Nodvy laddad för {display_name}")
