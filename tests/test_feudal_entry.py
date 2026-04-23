import importlib
import sys
from pathlib import Path


def test_feudal_runtime_paths_include_project_and_src():
    module = importlib.import_module("src.Feudal")
    module._ensure_runtime_paths()

    project_root = str(Path(__file__).resolve().parent.parent)
    src_root = str(Path(project_root) / "src")

    assert project_root in sys.path
    assert src_root in sys.path
