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


class _FakeApp:
    def __init__(self):
        self.world_data = {"nodes": {"2": {"node_id": 2}}}

    def add_status_message(self, _msg):
        pass


class _FakeInteractiveTree(_FakeTree):
    def __init__(self):
        super().__init__()
        self._focus = "1"
        self._selection = ()

    def identify_row(self, y):
        return "2" if y == 22 else ""

    def focus(self, item=None):
        if item is not None:
            self._focus = item
        return self._focus

    def selection_set(self, item):
        self._selection = (item,)

    def selection(self):
        return self._selection

    def exists(self, item):
        return item in {"1", "2"}


def test_bind_left_click_uses_single_click_event():
    tree = _FakeTree()
    view = StructureView(app=object(), parent=_FakePanel(), tree_widget=tree)

    view.bind_left_click(lambda _node_id: None)

    assert "<Button-1>" in tree.bindings


def test_left_click_activates_clicked_node_without_second_click():
    tree = _FakeInteractiveTree()
    app = _FakeApp()
    view = StructureView(app=app, parent=_FakePanel(), tree_widget=tree)
    opened = []
    view.bind_left_click(lambda node_id: opened.append(node_id))

    event = type("E", (), {"y": 22})()
    view._on_left_click(event)

    assert opened == [2]
    assert tree.selection() == ("2",)
    assert tree.focus() == "2"
