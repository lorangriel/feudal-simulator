from __future__ import annotations

import tkinter as tk
from typing import Callable, Iterable, Literal


class StructureView:
    def __init__(self, app, parent, tree_widget=None) -> None:
        self.app = app
        self.parent = parent
        self.panel = parent
        self.tree = tree_widget or getattr(parent, "tree", None)
        self.mode: Literal["admin", "province"] = "admin"
        self.current_province_owner_id: int | None = None
        self._admin_tree_state: dict[str, object] | None = None
        self._double_click_callback: Callable[[int], None] | None = None

    # --- Public API ---
    def capture_selection_and_expansion(self) -> dict:
        """Return current open items and selection as a serializable dict."""

        if not self._tree_exists():
            return {"open_items": set(), "selection": ()}

        open_items: set[str] = set()

        def gather_open(item_id: str) -> None:
            try:
                if self.tree.item(item_id, "open"):
                    open_items.add(item_id)
                for child_id in self.tree.get_children(item_id):
                    gather_open(child_id)
            except tk.TclError:
                pass

        for top_item in self.tree.get_children():
            gather_open(top_item)

        selection = tuple(self.tree.selection())
        return {"open_items": open_items, "selection": selection}

    def restore_selection_and_expansion(
        self,
        state: dict | None,
        *,
        focus_id: int | str | None = None,
        expand_to_owner_anchor: bool = False,
    ) -> None:
        """Restore expansion/selection state and optionally focus a node."""

        if not self._tree_exists():
            return

        open_items = set((state or {}).get("open_items", set()))
        selection = tuple((state or {}).get("selection", ()))

        for top_item in self.tree.get_children():
            self._apply_open_state(top_item, open_items)

        self._restore_selection(selection)

        focus_iid = str(focus_id) if focus_id is not None else None
        lineage = self._lineage(focus_iid)

        for ancestor in lineage:
            self._open_iid(ancestor)
        if focus_iid:
            self._open_iid(focus_iid)

        if expand_to_owner_anchor:
            self._expand_owner_anchor(focus_iid)

        target = self._first_existing_target(focus_iid, lineage)
        if target:
            try:
                self.tree.selection_set(target)
                self.tree.focus(target)
                self.tree.see(target)
            except Exception:
                pass

    def rebuild_full_tree(self) -> None:
        """Rebuild the tree according to current mode while keeping state."""

        self._render_current_view(self.capture_selection_and_expansion())

    def refresh_after_owner_change(self, province_id: int | str) -> None:
        """Refresh the tree after an owner change event."""

        if not self._tree_exists():
            return

        self.app.clear_depth_cache()
        self._render_current_view()

    def refresh_tree_item(self, node_id) -> None:
        """Update a specific tree item label and tags."""

        if not self._tree_exists():
            return

        node_id_str = str(node_id)
        if self.tree.exists(node_id_str):
            node_data = (self.app.world_data or {}).get("nodes", {}).get(node_id_str)
            if node_data:
                depth = self.app.get_depth_of_node(node_id)
                display_name = self.app.get_display_name_for_node(node_data, depth)
                try:
                    is_personal = (
                        str(node_data.get("owner_assigned_level", "none")) != "none"
                    )
                    self.tree.item(
                        node_id_str,
                        text=self.panel.format_node_label(display_name, is_personal),
                        tags=tuple(
                            [f"depth_{depth}"]
                            + (["personal_province"] if is_personal else [])
                        ),
                    )
                except tk.TclError:
                    return

    def set_mode(
        self, mode: Literal["admin", "province"], owner_id: int | None = None
    ) -> None:
        """Switch between admin and province modes."""

        if mode == "province":
            if owner_id is None:
                return
            if self.mode != "province":
                self._admin_tree_state = self.capture_selection_and_expansion()
            self.mode = "province"
            self.current_province_owner_id = owner_id
            self.panel.update_mode("province")
            self._render_province_subtrees(owner_id)
        else:
            restore_state = self._admin_tree_state
            self.mode = "admin"
            self.current_province_owner_id = None
            self.panel.update_mode("admin")
            self._admin_tree_state = None
            self._render_admin_tree(restore_state)

        if hasattr(self.app, "on_tree_selection_change"):
            try:
                self.app.on_tree_selection_change()
            except Exception:
                pass

    def bind_double_click(self, callback: Callable[[int], None]) -> None:
        """Bind double-click events to the provided callback."""

        self._double_click_callback = callback
        if self._tree_exists():
            self.tree.bind("<Double-1>", self._on_double_click)

    # --- Internal rendering helpers ---
    def _render_current_view(self, restore_state: dict | None = None) -> None:
        if self.mode == "province" and self.current_province_owner_id is not None:
            self._render_province_subtrees(self.current_province_owner_id, restore_state)
            return
        self._render_admin_tree(restore_state)

    def _render_admin_tree(self, restore_state: dict | None = None) -> None:
        if not self._tree_exists():
            return

        state = restore_state or self.capture_selection_and_expansion()
        self.tree.delete(*self.tree.get_children())

        world_data = self.app.world_data or {}
        if not world_data or not world_data.get("nodes"):
            return

        root_nodes_data = []
        node_dict = world_data.get("nodes", {})
        all_node_ids_in_dict = {int(k) for k in node_dict.keys() if str(k).isdigit()}

        for node_id_int in all_node_ids_in_dict:
            node_data = node_dict.get(str(node_id_int))
            if node_data and node_data.get("parent_id") is None:
                if node_data.get("node_id") != node_id_int:
                    node_data["node_id"] = node_id_int
                root_nodes_data.append(node_data)

        if not root_nodes_data:
            for node_id_int in all_node_ids_in_dict:
                node_data = node_dict.get(str(node_id_int))
                parent_id = node_data.get("parent_id") if node_data else None
                if node_data and parent_id is not None and parent_id not in all_node_ids_in_dict:
                    node_data["parent_id"] = None
                    if node_data.get("node_id") != node_id_int:
                        node_data["node_id"] = node_id_int
                    root_nodes_data.append(node_data)

        if not root_nodes_data:
            self.app.add_status_message(
                "Fel: Ingen rotnod (med parent_id=null eller ogiltigt parent_id) hittades."
            )
            return
        elif len(root_nodes_data) > 1:
            self.app.add_status_message(
                f"Varning: Flera ({len(root_nodes_data)}) rotnoder hittades. Visar alla."
            )

        root_nodes_data.sort(key=lambda n: n.get("node_id", 0))

        for root_node in root_nodes_data:
            self._add_tree_node_recursive("", root_node)

        self.restore_selection_and_expansion(state)

    def _add_tree_node_recursive(self, parent_iid, node_data):
        node_id = node_data.get("node_id")
        if node_id is None:
            print(f"Warning: Skipping node data without node_id: {node_data}")
            return

        node_id_str = str(node_id)
        if self.tree.exists(node_id_str):
            return

        depth = self.app.get_depth_of_node(node_id)
        display_name = self.app.get_display_name_for_node(node_data, depth)

        try:
            is_personal = str(node_data.get("owner_assigned_level", "none")) != "none"
            tags = [f"depth_{depth}"]
            if is_personal:
                tags.append("personal_province")
            self.tree.insert(
                parent_iid,
                "end",
                iid=node_id_str,
                text=self.panel.format_node_label(display_name, is_personal),
                open=(depth < 1),
                tags=tuple(tags),
            )
        except tk.TclError as e:
            print(
                f"Warning: Failed to insert node {node_id_str} ('{display_name}') into tree. Error: {e}"
            )
            return

        children_ids = node_data.get("children", [])
        if children_ids:
            child_nodes = []
            valid_children_ids = []
            for cid in children_ids:
                child_data = (self.app.world_data or {}).get("nodes", {}).get(str(cid))
                if child_data:
                    if child_data.get("node_id") != cid:
                        child_data["node_id"] = cid
                    child_nodes.append(child_data)
                    valid_children_ids.append(cid)

            child_nodes.sort(key=lambda n: self.app.get_display_name_for_node(n, depth + 1))
            for child_node in child_nodes:
                self._add_tree_node_recursive(node_id_str, child_node)
            node_data["children"] = valid_children_ids

    def _render_province_subtrees(
        self, owner_id: int | None, restore_state: dict | None = None
    ) -> None:
        if not self._tree_exists():
            return

        self.tree.delete(*self.tree.get_children())

        if owner_id is None or not self.app.world_data:
            return

        owner_level = self.app.get_depth_of_node(owner_id)
        owner_data = (self.app.world_data or {}).get("nodes", {}).get(str(owner_id), {})
        owner_name = self.app.get_display_name_for_node(owner_data, owner_level)

        anchor_iid = self._insert_owner_anchor(owner_id, owner_name, owner_level)
        if not anchor_iid:
            return

        province_subtrees = self.app.get_province_subtree(owner_id)
        if not isinstance(province_subtrees, list):
            province_subtrees = []

        for subtree in province_subtrees:
            self._insert_province_subtree(anchor_iid, subtree)

        if restore_state:
            self.restore_selection_and_expansion(
                restore_state,
                focus_id=owner_id,
                expand_to_owner_anchor=True,
            )

    def _insert_province_subtree(self, parent_iid: str, subtree: dict) -> None:
        node_id = subtree.get("id") if isinstance(subtree, dict) else None
        if node_id is None:
            return

        node_id_str = str(node_id)
        node_data = (self.app.world_data or {}).get("nodes", {}).get(node_id_str, {})
        depth = self.app.get_depth_of_node(node_id)
        display_name = self.app.get_display_name_for_node(node_data, depth)
        is_personal = str(node_data.get("owner_assigned_level", "none")) != "none"

        tags = [f"depth_{depth}"]
        if is_personal:
            tags.append("personal_province")

        try:
            self.tree.insert(
                parent_iid,
                "end",
                iid=node_id_str,
                text=self.panel.format_node_label(display_name, is_personal),
                open=(depth < 1),
                tags=tuple(tags),
            )
        except tk.TclError:
            return

        for child in subtree.get("children", []):
            self._insert_province_subtree(node_id_str, child)

    # --- Double-click handling ---
    def _on_double_click(self, _event):
        if not self._tree_exists() or not self.app.world_data:
            return

        item_id_str = self.tree.focus()
        if not item_id_str:
            return

        if not self.tree.exists(item_id_str):
            self.app.add_status_message(
                f"Fel: Trädnod ID {item_id_str} finns inte längre."
            )
            return

        try:
            node_id = int(item_id_str)
        except (TypeError, ValueError):
            return

        node_data = (self.app.world_data or {}).get("nodes", {}).get(item_id_str)
        if not node_data:
            self.app.add_status_message(
                f"Fel: Kunde inte hitta data för nod ID {item_id_str}"
            )
            return

        if self._double_click_callback:
            self._double_click_callback(node_id)

    # --- State helpers ---
    def _tree_exists(self) -> bool:
        return bool(getattr(self, "tree", None)) and self.tree.winfo_exists()

    def _apply_open_state(self, item_id: str, open_items: set[str]) -> None:
        try:
            if self.tree.exists(item_id):
                self.tree.item(item_id, open=item_id in open_items)
                for child_id in self.tree.get_children(item_id):
                    self._apply_open_state(child_id, open_items)
        except tk.TclError:
            pass

    def _restore_selection(self, selection: Iterable[str]) -> None:
        if not selection:
            return
        try:
            valid_selection = tuple(s for s in selection if self.tree.exists(s))
            if valid_selection:
                self.tree.selection_set(valid_selection)
                self.tree.focus(valid_selection[0])
                self.tree.see(valid_selection[0])
        except tk.TclError:
            print("Warning: Could not fully restore tree selection (items might have changed).")

    def _lineage(self, node_id: str | None) -> list[str]:
        if node_id is None:
            return []
        nodes = getattr(self.app, "world_data", {}) or {}
        nodes_dict = nodes.get("nodes", {}) if isinstance(nodes, dict) else {}
        lineage: list[str] = []
        current: str | None = str(node_id)

        while current is not None:
            node_data = nodes_dict.get(str(current))
            if not node_data:
                break
            parent_raw = node_data.get("parent_id")
            if parent_raw is None:
                break
            parent_id = str(parent_raw)
            lineage.insert(0, parent_id)
            current = parent_id
        return lineage

    def _first_existing_target(
        self, focus_iid: str | None, lineage: Iterable[str]
    ) -> str | None:
        if focus_iid and self.tree.exists(focus_iid):
            return focus_iid

        for ancestor in lineage:
            if self.tree.exists(ancestor):
                return ancestor

        roots = self.tree.get_children("")
        return roots[0] if roots else None

    def _open_iid(self, iid: str) -> None:
        try:
            if self.tree.exists(iid):
                self.tree.item(iid, open=True)
        except Exception:
            pass

    def _expand_owner_anchor(self, focus_iid: str | None) -> None:
        if focus_iid is None:
            return

        nodes = getattr(self.app, "world_data", {}) or {}
        nodes_dict = nodes.get("nodes", {}) if isinstance(nodes, dict) else {}
        node_data = nodes_dict.get(str(focus_iid))
        if not node_data:
            return

        owner_id = node_data.get("owner_assigned_id")
        anchor_iid = self._province_anchor_iid(owner_id)
        if anchor_iid and self.tree.exists(anchor_iid):
            self._open_iid(anchor_iid)

    def _province_anchor_iid(self, owner_id: int | None) -> str:
        if owner_id is None:
            return ""
        return f"{self.app.PROVINCE_ANCHOR_IID}{owner_id}"

    def _insert_owner_anchor(
        self, owner_id: int, owner_name: str, owner_level: int
    ) -> str:
        iid = self._province_anchor_iid(owner_id)
        if not iid:
            return ""

        if self.tree.exists(iid):
            try:
                self.tree.delete(iid)
            except tk.TclError:
                pass

        anchor_label = f"Ägare: {owner_name} (nivå {owner_level})"

        try:
            self.tree.insert("", "end", iid=iid, text=anchor_label, open=True)
            return iid
        except tk.TclError:
            return ""

