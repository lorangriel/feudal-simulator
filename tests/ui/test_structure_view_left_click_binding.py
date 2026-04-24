from src.ui.views.structure_view import StructureView


class _FakeTree:
    def __init__(self):
        self.bindings = {}

    def bind(self, event_name, callback):
        self.bindings[event_name] = callback

    def winfo_exists(self):
        return True


class _FakePanel:
    pass


def test_bind_left_click_uses_single_click_event():
    tree = _FakeTree()
    view = StructureView(app=object(), parent=_FakePanel(), tree_widget=tree)

    view.bind_left_click(lambda _node_id: None)

    assert "<Button-1>" in tree.bindings
