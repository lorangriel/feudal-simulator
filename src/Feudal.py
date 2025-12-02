"""Officiell startfil för feodal-simulatorn."""
from __future__ import annotations

try:
    from src.ui import app as ui_app
except ImportError:
    from ui import app as ui_app

main = ui_app.main


if __name__ == "__main__":
    main()
