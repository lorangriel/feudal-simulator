import pytest

from dynamic_map import DynamicMapCanvas


class DummyCanvas:
    def __init__(self):
        self.width = 500
        self.height = 300
        self.scale_calls = []

    def winfo_width(self):
        return self.width

    def winfo_height(self):
        return self.height

    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def scale(self, tag, x, y, sx, sy):
        self.scale_calls.append((tag, x, y, sx, sy))


def test_set_world_data():
    canvas = DynamicMapCanvas(None, None, {"nodes": {}})
    new_data = {"nodes": {"1": {"node_id": 1}}}
    canvas.set_world_data(new_data)
    assert canvas.world_data is new_data


def test_on_dynamic_map_zoom():
    canvas = DynamicMapCanvas(None, None, None)
    canvas.canvas = DummyCanvas()

    event = type("Evt", (), {"delta": 120, "num": 0})()
    canvas.on_dynamic_map_zoom(event)
    assert canvas.dynamic_scale == pytest.approx(1.1)
    assert canvas.canvas.scale_calls[0] == ("all", 250.0, 150.0, 1.1, 1.1)

    canvas.dynamic_scale = 0.11
    event_neg = type("Evt", (), {"delta": -120, "num": 0})()
    canvas.on_dynamic_map_zoom(event_neg)
    assert canvas.dynamic_scale == pytest.approx(0.1)
