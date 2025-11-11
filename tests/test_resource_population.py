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
    def trace_add(self, _mode, callback):
        self._callbacks.append(callback)

class DummyWidget:
    def __init__(self, *args, **kwargs):
        pass
    def grid(self, *a, **k):
        return self
    def pack(self, *a, **k):
        return self
    def grid_remove(self, *a, **k):
        return self
    def configure(self, *a, **k):
        return self
    config = configure
    def state(self, *a, **k):
        return self
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
    def winfo_children(self):
        return []
    def yview(self, *a, **k):
        return None
    def xview(self, *a, **k):
        return None
    def add(self, *a, **k):
        return self

class DummyTkModule(types.SimpleNamespace):
    StringVar = DummyVar
    Listbox = DummyWidget
    TclError = Exception
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    END = "end"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class DummyTtkModule(types.SimpleNamespace):
    Frame = DummyWidget
    Label = DummyWidget
    Entry = DummyWidget
    Combobox = DummyWidget
    Button = DummyWidget
    Separator = DummyWidget
    Notebook = DummyWidget

class DummyMessageBox(types.SimpleNamespace):
    askyesno = staticmethod(lambda *a, **k: True)
    showerror = staticmethod(lambda *a, **k: None)

def make_sim(monkeypatch, world):
    sim = fs.FeodalSimulator.__new__(fs.FeodalSimulator)
    sim.world_data = world
    sim.world_manager = fs.WorldManager(world)
    sim.pending_save_callback = None
    sim.save_current_world = lambda: None
    sim.add_status_message = lambda *a, **k: None
    sim.refresh_tree_item = lambda *a, **k: None
    sim.store_tree_state = lambda: (set(), ())
    sim.populate_tree = lambda: None
    sim.restore_tree_state = lambda *a, **k: None
    sim.root = None
    sim.tree = type("T", (), {"winfo_exists": lambda self: False})()
    monkeypatch.setattr(fs, "tk", DummyTkModule())
    monkeypatch.setattr(fs, "ttk", DummyTtkModule())
    monkeypatch.setattr(fs, "messagebox", DummyMessageBox())
    return sim


def test_resource_population_preserved(monkeypatch):
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": 0,
                "res_type": "Resurs",
                "custom_name": "",
                "population": 5,
                "children": [],
            }
        },
        "characters": {},
    }
    sim = make_sim(monkeypatch, world)
    parent = DummyWidget()
    sim._show_resource_editor(parent, world["nodes"]["1"], depth=4)
    sim.commit_pending_changes()
    assert world["nodes"]["1"]["population"] == 5


def test_noble_family_type_removed_at_depth_four(monkeypatch):
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": 0,
                "res_type": "Adelsfamilj",
                "custom_name": "Familjen Ek",
                "population": 0,
                "children": [],
            }
        },
        "characters": {},
    }
    sim = make_sim(monkeypatch, world)
    parent = DummyWidget()
    sim._show_resource_editor(parent, world["nodes"]["1"], depth=4)
    assert world["nodes"]["1"]["res_type"] != "Adelsfamilj"


def test_noble_family_type_allowed_at_depth_five(monkeypatch):
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": 0,
                "res_type": "Adelsfamilj",
                "custom_name": "Familjen Ek",
                "population": 0,
                "children": [],
            }
        },
        "characters": {},
    }
    sim = make_sim(monkeypatch, world)
    parent = DummyWidget()
    sim._show_resource_editor(parent, world["nodes"]["1"], depth=5)
    assert world["nodes"]["1"]["res_type"] == "Adelsfamilj"
