import types
import feodal_simulator as fs

class DummyVar:
    def __init__(self, value=""):
        self._value = value
        self._callbacks = []
    def get(self):
        return self._value
    def set(self, value):
        self._value = value
        for cb in self._callbacks:
            cb(None, None, None)
    def trace_add(self, _mode, cb):
        self._callbacks.append(cb)

class TrackingWidget:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.grid_calls = 0
        self.grid_remove_calls = 0
    def grid(self, *a, **k):
        self.grid_calls += 1
        return self
    def grid_remove(self, *a, **k):
        self.grid_remove_calls += 1
        return self
    def pack(self, *a, **k):
        return self
    def pack_forget(self, *a, **k):
        return self
    def configure(self, *a, **k):
        return self
    config = configure
    def bind(self, *a, **k):
        return self
    def insert(self, *a, **k):
        return self
    def delete(self, *a, **k):
        return self
    def set(self, *a, **k):
        return self
    def get(self, *a, **k):
        return ""
    def curselection(self):
        return ()
    def grid_columnconfigure(self, *a, **k):
        return None
    def grid_rowconfigure(self, *a, **k):
        return None
    def columnconfigure(self, *a, **k):
        return None
    def rowconfigure(self, *a, **k):
        return None
    def winfo_exists(self):
        return True
    def yview(self, *a, **k):
        return None
    def xview(self, *a, **k):
        return None

class DummyTkModule(types.SimpleNamespace):
    StringVar = DummyVar
    TclError = Exception
    LEFT = "left"
    HORIZONTAL = "horizontal"

captured = {}

def label_factory(*args, **kwargs):
    w = TrackingWidget(*args, **kwargs)
    if kwargs.get("text") == "Slag:":
        captured["label"] = w
    return w

def entry_factory(*args, **kwargs):
    w = TrackingWidget(*args, **kwargs)
    if kwargs.get("state") == "readonly" and kwargs.get("width") == 12:
        captured["entry"] = w
    return w

class DummyTtkModule(types.SimpleNamespace):
    Frame = TrackingWidget
    Label = staticmethod(label_factory)
    Entry = staticmethod(entry_factory)
    Combobox = TrackingWidget
    Button = TrackingWidget
    Separator = TrackingWidget

class DummyMessageBox(types.SimpleNamespace):
    askyesno = staticmethod(lambda *a, **k: True)
    showerror = staticmethod(lambda *a, **k: None)


def make_sim(monkeypatch, node_data):
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = {"nodes": {str(node_data["node_id"]): node_data}}
    sim.world_manager = fs.WorldManager(sim.world_data)
    sim.pending_save_callback = None
    sim.save_current_world = lambda: None
    sim.add_status_message = lambda *a, **k: None
    sim.refresh_tree_item = lambda *a, **k: None
    sim.store_tree_state = lambda: (set(), ())
    sim.populate_tree = lambda: None
    sim.restore_tree_state = lambda *a, **k: None
    sim.root = None
    sim.tree = type("T", (), {"winfo_exists": lambda self: False})()
    sim._auto_save_field = lambda *a, **k: None

    monkeypatch.setattr(fs, "tk", DummyTkModule())
    monkeypatch.setattr(fs, "ttk", DummyTtkModule())
    monkeypatch.setattr(fs, "messagebox", DummyMessageBox())
    return sim


def test_rolls_field_visibility(monkeypatch):
    node = {"node_id": 1, "res_type": "Gods", "children": []}
    sim = make_sim(monkeypatch, node)
    parent = TrackingWidget()
    sim._show_resource_editor(parent, node, depth=4)
    assert captured["label"].grid_remove_calls > 0
    assert captured["entry"].grid_remove_calls > 0

    captured.clear()
    node2 = {"node_id": 1, "res_type": "Väder", "children": []}
    sim = make_sim(monkeypatch, node2)
    parent = TrackingWidget()
    sim._show_resource_editor(parent, node2, depth=4)
    assert captured["label"].grid_remove_calls == 0
    assert captured["entry"].grid_remove_calls == 0
