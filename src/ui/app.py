"""Applikationsskal för feodal-simulatorns huvud-UI."""
from __future__ import annotations

import tkinter as tk

from feodal_simulator import FeodalSimulator


def create_app(root: tk.Misc | None = None) -> FeodalSimulator:
    root = root or tk.Tk()
    return FeodalSimulator(root)


def main() -> None:
    root = tk.Tk()
    create_app(root)
    root.mainloop()


__all__ = ["create_app", "main", "FeodalSimulator"]
