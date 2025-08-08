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
    def pack_forget(self, *a, **k):
        return self


class DummyText(DummyWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = ""
        self.modified = False
        self.bindings = {}
    def insert(self, index, text):
        if index == "1.0":
            self.content = text + self.content
        else:
            self.content += text
    def delete(self, start, end=None):
        self.content = ""
    def get(self, start, end):
        return self.content
    def index(self, pos):
        if pos == "end-1c":
            lines = self.content.count("\n") + 1
            return f"{lines}.0"
        return "1.0"
    def edit_modified(self, flag=None):
        if flag is None:
            return self.modified
        self.modified = flag
    def bind(self, event, callback):
        self.bindings[event] = callback
    def yview_scroll(self, *a, **k):
        return None


class DummyScrollbar(DummyWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = None
    def config(self, **kwargs):
        self.command = kwargs.get("command", self.command)
        return self


class DummyTkModule(types.SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.vars = []
        self.last_text = None
        self.StringVar = self._StringVar
        self.Text = self._Text
        self.Listbox = DummyWidget
        self.TclError = Exception
        self.LEFT = "left"
        self.RIGHT = "right"
        self.TOP = "top"
        self.BOTTOM = "bottom"
        self.END = "end"
        self.BOTH = "both"
        self.Y = "y"
        self.HORIZONTAL = "horizontal"
        self.VERTICAL = "vertical"
    def _StringVar(self, value=""):
        var = DummyVar(value)
        self.vars.append(var)
        return var
    def _Text(self, *a, **k):
        t = DummyText()
        self.last_text = t
        return t


class DummyTtkModule(types.SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.Frame = DummyWidget
        self.Label = DummyWidget
        self.Entry = DummyWidget
        self.Combobox = DummyWidget
        self.Button = DummyWidget
        self.Separator = DummyWidget
        self.Scrollbar = DummyScrollbar


class DummyMessageBox(types.SimpleNamespace):
    askyesno = staticmethod(lambda *a, **k: True)
    showerror = staticmethod(lambda *a, **k: None)


def make_sim(monkeypatch, world):
    dummy_tk = DummyTkModule()
    dummy_ttk = DummyTtkModule()
    monkeypatch.setattr(fs, "tk", dummy_tk)
    monkeypatch.setattr(fs, "ttk", dummy_ttk)
    monkeypatch.setattr(fs, "messagebox", DummyMessageBox())
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
    return sim, dummy_tk


def test_lager_free_text(monkeypatch):
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": 0,
                "res_type": "Lager",
                "lager_text": "",
                "storage_basic": 0,
                "storage_luxury": 0,
                "storage_silver": 0,
                "storage_timber": 0,
                "storage_coal": 0,
                "storage_iron_ore": 0,
                "storage_iron": 0,
                "storage_animal_feed": 0,
                "storage_skin": 0,
            }
        },
        "characters": {},
    }
    sim, dummy_tk = make_sim(monkeypatch, world)
    parent = DummyWidget()
    sim._show_resource_editor(parent, world["nodes"]["1"], depth=4)
    text_widget = dummy_tk.last_text
    text_widget.delete("1.0", "end")
    text_widget.insert("1.0", "rad1\nrad2\nrad3\nrad4\nrad5")
    text_widget.edit_modified(True)
    text_widget.bindings["<<Modified>>"](None)
    assert world["nodes"]["1"]["lager_text"] == "rad1\nrad2\nrad3\nrad4\nrad5"


def test_lager_storage_variables(monkeypatch):
    world = {
        "nodes": {
            "1": {
                "node_id": 1,
                "parent_id": 0,
                "res_type": "Lager",
                "lager_text": "",
                "storage_basic": 0,
                "storage_luxury": 0,
                "storage_silver": 0,
                "storage_timber": 0,
                "storage_coal": 0,
                "storage_iron_ore": 0,
                "storage_iron": 0,
                "storage_animal_feed": 0,
                "storage_skin": 0,
            }
        },
        "characters": {},
    }
    sim, dummy_tk = make_sim(monkeypatch, world)
    parent = DummyWidget()
    sim._show_resource_editor(parent, world["nodes"]["1"], depth=4)
    bas_var = dummy_tk.vars[1]
    assert bas_var.get() == "0/BAS"
    bas_var.set("7/BAS")
    assert world["nodes"]["1"]["storage_basic"] == "7"
