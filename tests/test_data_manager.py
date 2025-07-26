import json
from src import data_manager


def test_load_worlds_from_file_success(tmp_path, monkeypatch):
    data = {"a": 1}
    f = tmp_path / "worlds.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(data_manager, "DEFAULT_WORLDS_FILE", str(f))
    called = []
    monkeypatch.setattr(data_manager.messagebox, "showerror", lambda *a, **k: called.append(True))
    result = data_manager.load_worlds_from_file()
    assert result == data
    assert not called


def test_load_worlds_from_file_missing(tmp_path, monkeypatch):
    f = tmp_path / "missing.json"
    monkeypatch.setattr(data_manager, "DEFAULT_WORLDS_FILE", str(f))
    called = []
    monkeypatch.setattr(data_manager.messagebox, "showerror", lambda *a, **k: called.append(True))
    result = data_manager.load_worlds_from_file()
    assert result == {}
    assert not called


def test_load_worlds_from_file_error(tmp_path, monkeypatch):
    f = tmp_path / "bad.json"
    f.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(data_manager, "DEFAULT_WORLDS_FILE", str(f))
    def bad_load(_):
        raise ValueError("boom")
    monkeypatch.setattr(data_manager.WorldInterface, "load_worlds_file", bad_load)
    called = []
    monkeypatch.setattr(data_manager.messagebox, "showerror", lambda *a, **k: called.append(True))
    result = data_manager.load_worlds_from_file()
    assert result == {}
    assert called


def test_save_worlds_to_file_success(tmp_path, monkeypatch):
    f = tmp_path / "out.json"
    monkeypatch.setattr(data_manager, "DEFAULT_WORLDS_FILE", str(f))
    saved = {}
    def fake_save(data, path):
        saved["data"] = data
        saved["path"] = path
    monkeypatch.setattr(data_manager.WorldInterface, "save_worlds_file", fake_save)
    called = []
    monkeypatch.setattr(data_manager.messagebox, "showerror", lambda *a, **k: called.append(True))
    data_manager.save_worlds_to_file({"x": 2})
    assert saved == {"data": {"x": 2}, "path": str(f)}
    assert not called


def test_save_worlds_to_file_error(tmp_path, monkeypatch):
    f = tmp_path / "out.json"
    monkeypatch.setattr(data_manager, "DEFAULT_WORLDS_FILE", str(f))
    def bad_save(data, path):
        raise IOError("fail")
    monkeypatch.setattr(data_manager.WorldInterface, "save_worlds_file", bad_save)
    called = []
    monkeypatch.setattr(data_manager.messagebox, "showerror", lambda *a, **k: called.append(True))
    data_manager.save_worlds_to_file({})
    assert called
