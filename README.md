# feudal-simulator
[![codecov](https://codecov.io/gh/lorangriel/feudal-simulator/branch/main/graph/badge.svg)](https://codecov.io/gh/lorangriel/feudal-simulator)

This project is a small prototype for a feudal county simulation. The code
is split across multiple modules under `src/`.

Run the original Tkinter GUI application with:

```
python src/simulator.py
```

A minimal HTTP server that renders the same data as HTML is also available.
Start it with:

```
python src/http_server.py
```

Then open `http://localhost:8000` in a browser.

## Dual Map Tool
A lightweight mapper with two synchronised views lives in `src/dual_map_tool.py`.
Start it with:

```bash
python src/dual_map_tool.py
```

Map A shows a hex grid. Drag hexes with the left mouse button to move
them, use the colour palette on the right to recolour a hex and
right‑click an edge to assign a border type. Map B groups the same nodes
by overlord. Switch views using the tabs at the top. Zoom with the mouse
wheel and pan by dragging with the middle mouse button.

## Testing
Run `pytest` in the repository root to execute the automated test suite.
