"""Helpers för Struktur-vy-state och refreshlogik."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class StructureViewState:
    open_items: set[str]
    selection: tuple[str, ...]


class StructureView:
    def __init__(self, app) -> None:
        self.app = app

    def capture_selection_and_expansion(self) -> StructureViewState:
        open_items, selection = self.app.store_tree_state()
        return StructureViewState(set(open_items), tuple(selection))

    def refresh_after_owner_change(self, province_id: str | int) -> None:
        if not getattr(self.app, "tree", None) or not self.app.tree.winfo_exists():
            return
        self.app.clear_depth_cache()
        self.app._refresh_structure_view()

    def restore_selection_and_expansion(
        self,
        snapshot: StructureViewState | None,
        focus_id: str | int | None,
        expand_to_owner_anchor: bool = False,
    ) -> None:
        if not getattr(self.app, "tree", None) or not self.app.tree.winfo_exists():
            return

        if snapshot is not None:
            self.app.restore_tree_state(snapshot.open_items, snapshot.selection)

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
                self.app.tree.selection_set(target)
                self.app.tree.focus(target)
                self.app.tree.see(target)
            except Exception:
                pass

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
        if focus_iid and self.app.tree.exists(focus_iid):
            return focus_iid

        for ancestor in lineage:
            if self.app.tree.exists(ancestor):
                return ancestor

        roots = self.app.tree.get_children("")
        return roots[0] if roots else None

    def _open_iid(self, iid: str) -> None:
        try:
            if self.app.tree.exists(iid):
                self.app.tree.item(iid, open=True)
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
        anchor_iid = self.app._province_anchor_iid(owner_id)
        if anchor_iid and self.app.tree.exists(anchor_iid):
            self._open_iid(anchor_iid)
