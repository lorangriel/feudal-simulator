from src.ui.views.structure_view import StructureView


class _FakeTree:
    def __init__(self):
        self.nodes = {
            "1": {"children": ["2"], "open": False},
            "2": {"children": ["3"], "open": False},
            "3": {"children": [], "open": False},
        }
        self._selection = ()
        self._focus = ""
        self.last_seen = ""

    def winfo_exists(self):
        return True

    def get_children(self, item_id=""):
        if item_id == "":
            children = []
            for node_id in self.nodes:
                if self.parent(node_id) is None:
                    children.append(node_id)
            return tuple(children)
        node = self.nodes.get(item_id)
        if not node:
            return ()
        return tuple(node["children"])

    def parent(self, node_id):
        for parent_id, node in self.nodes.items():
            if node_id in node["children"]:
                return parent_id
        return None

    def item(self, item_id, option=None, **kwargs):
        node = self.nodes[item_id]
        if "open" in kwargs:
            node["open"] = kwargs["open"]
        if option == "open":
            return node["open"]
        return node

    def exists(self, item_id):
        return item_id in self.nodes

    def selection(self):
        return self._selection

    def selection_set(self, selection):
        if isinstance(selection, tuple):
            self._selection = selection
        else:
            self._selection = (selection,)

    def focus(self, item_id=None):
        if item_id is not None:
            self._focus = item_id
        return self._focus

    def see(self, item_id):
        self.last_seen = item_id


class _FakePanel:
    pass


class _FakeApp:
    def __init__(self):
        self.world_data = {
            "nodes": {
                "1": {"parent_id": None},
                "2": {"parent_id": 1},
                "3": {"parent_id": 2},
            }
        }


def test_restore_keeps_existing_selection():
    tree = _FakeTree()
    view = StructureView(app=_FakeApp(), parent=_FakePanel(), tree_widget=tree)

    view.restore_selection_and_expansion({"open_items": set(), "selection": ("2",)})

    assert tree.selection() == ("2",)


def test_restore_selects_nearest_parent_when_selected_node_is_missing():
    tree = _FakeTree()
    tree.nodes.pop("3")
    view = StructureView(app=_FakeApp(), parent=_FakePanel(), tree_widget=tree)

    view.restore_selection_and_expansion({"open_items": set(), "selection": ("3",)})

    assert tree.selection() == ("2",)
