"""Global safe Combobox behavior for the Feodal simulator UI."""
from __future__ import annotations

import logging
import sys
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)

_PATCHED = False


class SafeCombobox(ttk.Combobox):
    """A ``ttk.Combobox`` that delays commits until the user confirms.

    Behaviour tweaks:
    * Mouse wheel does nothing while the dropdown is closed (event is forwarded
      to the toplevel so outer scroll areas still react).
    * While the dropdown is open, the wheel only moves the highlighted option; a
      commit happens when the user confirms (click/Enter/closing with a pending
      choice). ESC restores the previously committed value.
    """

    POLL_INTERVAL_MS = 80

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(takefocus=True)

        self._committed_value = self.get()
        self._pending_value: str | None = None
        self._pending_index: int | None = None
        self._dropdown_open = False
        self._cancelled = False
        self._popdown_widget: tk.Misc | None = None
        self._listbox_widget: tk.Misc | None = None
        self._listbox_bind_ids: dict[str, str] = {}
        self._state_poll_id: str | None = None

        self._install_bindings()
        self._start_state_poll()

    # ------------------------------------------------------------------
    # Public helpers (useful for tests)
    # ------------------------------------------------------------------
    @property
    def pending_value(self) -> str | None:
        return self._pending_value

    def is_dropdown_open(self) -> bool:
        return self._dropdown_open

    # ------------------------------------------------------------------
    # Binding setup
    # ------------------------------------------------------------------
    def _install_bindings(self) -> None:
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind(sequence, self._on_mousewheel, add="+")

        for sequence in ("<Return>", "<KP_Enter>"):
            self.bind(sequence, self._on_return, add="+")
        self.bind("<Escape>", self._on_escape, add="+")
        self.bind("<<ComboboxSelected>>", self._on_user_committed, add="+")

    def _start_state_poll(self) -> None:
        if self._state_poll_id is not None:
            return
        self._state_poll_id = self.after(self.POLL_INTERVAL_MS, self._watch_dropdown_state)

    # ------------------------------------------------------------------
    # Dropdown open/close tracking
    # ------------------------------------------------------------------
    def _watch_dropdown_state(self) -> None:
        try:
            open_now = self._detect_dropdown_open()
        except tk.TclError:
            return

        if open_now and not self._dropdown_open:
            self._on_dropdown_open()
        elif not open_now and self._dropdown_open:
            self._on_dropdown_close()

        try:
            self._state_poll_id = self.after(
                self.POLL_INTERVAL_MS, self._watch_dropdown_state
            )
        except tk.TclError:
            self._state_poll_id = None

    def _detect_dropdown_open(self) -> bool:
        popdown = self._get_popdown_widget()
        if popdown is None:
            return False
        try:
            return bool(popdown.winfo_ismapped())
        except tk.TclError:
            return False

    def _on_dropdown_open(self) -> None:
        self._dropdown_open = True
        self._cancelled = False
        self._pending_value = None
        self._pending_index = self.current() if self.current() >= 0 else 0
        self._popdown_widget = self._get_popdown_widget()
        self._listbox_widget = self._get_listbox_widget()

        self._log_debug("dropdown-open")

        if self._listbox_widget is not None and self._pending_index is not None:
            self._bind_listbox_events(self._listbox_widget)
            self._highlight_index(self._pending_index)

    def _on_dropdown_close(self) -> None:
        self._dropdown_open = False
        self._unbind_listbox_events()
        if self._cancelled:
            self._log_debug("dropdown-close-abort")
            self.set(self._committed_value)
            self._pending_value = None
            self._pending_index = None
            self._cancelled = False
            return

        if self._pending_value is not None and self._pending_value != self._committed_value:
            self._commit_pending_selection("close")
        self._pending_value = None
        self._pending_index = None
        self._log_debug("dropdown-close")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_mousewheel(self, event: tk.Event) -> str | None:
        if not self._dropdown_open:
            self._log_debug("wheel-ignored-closed")
            self._forward_to_toplevel(event)
            return "break"

        step = self._normalize_mousewheel_delta(event)
        if step == 0:
            return "break"

        self._adjust_pending_by_delta(step)
        return "break"

    def _on_return(self, _event: tk.Event) -> str | None:
        if self._dropdown_open and self._pending_value is not None:
            self._commit_pending_selection("enter")
            return "break"
        return None

    def _on_escape(self, _event: tk.Event) -> str | None:
        if self._dropdown_open:
            self._cancelled = True
            self._pending_value = None
            self._pending_index = None
            self.set(self._committed_value)
            self._log_debug("escape-abort")
            return None
        return None

    def _on_user_committed(self, _event: tk.Event) -> None:
        self._committed_value = self.get()
        self._pending_value = None
        self._pending_index = None
        self._cancelled = False
        self._log_debug("commit-event")

    # ------------------------------------------------------------------
    # Pending selection management
    # ------------------------------------------------------------------
    def _adjust_pending_by_delta(self, delta_steps: int) -> None:
        values = list(self.cget("values"))
        if not values:
            return
        current_index = self._pending_index
        if current_index is None:
            current_index = self.current()
            if current_index < 0:
                current_index = 0

        new_index = max(0, min(len(values) - 1, current_index + delta_steps))
        self._pending_index = new_index
        self._pending_value = values[new_index]
        self._highlight_index(new_index)
        self._log_debug(f"pending-index={new_index}")

    def _highlight_index(self, index: int) -> None:
        listbox = self._get_listbox_widget()
        if listbox is None:
            return
        try:
            listbox.selection_clear(0, "end")
            listbox.selection_set(index)
            listbox.activate(index)
            listbox.see(index)
        except tk.TclError:
            return

    def _commit_pending_selection(self, reason: str) -> None:
        if self._pending_value is None:
            return
        value = self._pending_value
        self.set(value)
        self._committed_value = value
        self._pending_value = None
        self._pending_index = None
        self._log_debug(f"commit-{reason}={value}")
        try:
            self.event_generate("<<ComboboxSelected>>")
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _normalize_mousewheel_delta(self, event: tk.Event) -> int:
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

    def _forward_to_toplevel(self, event: tk.Event) -> None:
        try:
            toplevel = self.winfo_toplevel()
        except tk.TclError:
            return

        sequence = "<MouseWheel>" if getattr(event, "delta", None) is not None else None
        if getattr(event, "num", None) in (4, 5):
            sequence = f"<Button-{event.num}>"

        if sequence is None:
            return

        try:
            if sequence == "<MouseWheel>":
                toplevel.event_generate(sequence, delta=getattr(event, "delta", 0))
            else:
                toplevel.event_generate(sequence)
        except tk.TclError:
            return

    def _get_popdown_widget(self) -> tk.Misc | None:
        try:
            popdown_path = self.tk.call("ttk::combobox::PopdownWindow", self._w)
        except tk.TclError:
            return None
        try:
            return self.nametowidget(popdown_path)
        except (tk.TclError, KeyError):
            return None

    def _get_listbox_widget(self) -> tk.Misc | None:
        if self._listbox_widget is not None:
            return self._listbox_widget
        popdown = self._get_popdown_widget()
        if popdown is None:
            return None
        try:
            listbox = popdown.nametowidget("f.l")
        except (tk.TclError, KeyError):
            return None
        self._listbox_widget = listbox
        return listbox

    def _bind_listbox_events(self, listbox: tk.Misc) -> None:
        self._listbox_bind_ids = {}
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self._listbox_bind_ids[sequence] = listbox.bind(
                sequence, self._on_mousewheel, add="+"
            )
        for sequence in ("<Return>", "<KP_Enter>"):
            self._listbox_bind_ids[sequence] = listbox.bind(
                sequence, self._on_return, add="+"
            )
        self._listbox_bind_ids["<Escape>"] = listbox.bind(
            "<Escape>", self._on_escape, add="+"
        )

    def _unbind_listbox_events(self) -> None:
        listbox = self._listbox_widget
        if listbox is None:
            return
        for sequence, funcid in self._listbox_bind_ids.items():
            try:
                listbox.unbind(sequence, funcid)
            except tk.TclError:
                pass
        self._listbox_bind_ids = {}

    def _log_debug(self, message: str) -> None:
        logger.debug("combobox %s: %s", self.winfo_name(), message)


def apply_safe_combobox_patch() -> None:
    """Replace ``ttk.Combobox`` globally with :class:`SafeCombobox`."""

    global _PATCHED
    if _PATCHED:
        return
    ttk.Combobox = SafeCombobox  # type: ignore
    _PATCHED = True
    logger.debug("Global safe combobox patch applied")

