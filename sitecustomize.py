"""Project-level sitecustomize to expose the bundled time package."""
from __future__ import annotations

import importlib
import sys
import importlib.util
import types
from pathlib import Path

_pkg_path = Path(__file__).parent / "src" / "time"

if _pkg_path.exists():
    builtin_time = importlib.import_module("time")
    current = sys.modules.get("time")
    needs_proxy = not getattr(current, "__path__", None) or getattr(
        getattr(current, "__spec__", None), "origin", ""
    ) == "built-in"
    if needs_proxy:
        proxy = types.ModuleType("time")
        proxy.__dict__.update({k: getattr(builtin_time, k) for k in dir(builtin_time)})

        def __getattr__(name, bt=builtin_time):
            return getattr(bt, name)

        proxy.__getattr__ = __getattr__
        proxy.__path__ = [str(_pkg_path)]
        proxy.__spec__ = importlib.util.spec_from_loader("time", loader=None, is_package=True)
        proxy.__file__ = str(_pkg_path / "__init__.py")
        sys.modules["time"] = proxy
