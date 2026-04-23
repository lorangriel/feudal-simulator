"""Officiell startfil för feodal-simulatorn."""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_runtime_paths() -> None:
    """Säkerställ att både projektrot och src-katalog finns på sys.path."""
    current_file = Path(__file__).resolve()
    src_root = current_file.parent
    project_root = src_root.parent
    for path in (project_root, src_root):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


_ensure_runtime_paths()

try:
    from src.ui import app as ui_app
except ImportError:
    from ui import app as ui_app

main = ui_app.main


if __name__ == "__main__":
    main()
