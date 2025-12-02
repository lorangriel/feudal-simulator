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

## Gränssnittspaneler
Det grafiska huvudfönstret använder tre namngivna paneler:

- **Struktur** – visar hierarkiträdet i vänsterkolumnen.
- **Status** – presenterar statusmeddelanden i den övre högra rutan.
- **Detaljer: <resursnamn>** – anger den valda noden eller resursen i den nedre högra rutan och uppdateras direkt när användaren byter val.

### Mushjul i Detaljer-panelen
- Mushjulsrörelser fångas globalt för hela Detaljer-panelens innehåll och normaliseras för `MouseWheel` (Windows/macOS) samt `Button-4`/`Button-5` (X11/Linux).
- Scrollningen driver panelens vertikala vy (canvas-backing) och fortsätter fungera även efter att innehållet har byggts om.
- Interna widgets med egen scroll (t.ex. `Text`) tar över hjulet; övriga ytor scrollar panelen.
- Använd `FeodalSimulator.create_details_scrollable_frame(...)` när ett scrollbart innehåll skapas i panelen så kopplas mushjulsbindningen in automatiskt.
- Tester kan köras headless med `pytest tests/test_details_scroll.py` och skippas automatiskt om ingen Tk-display finns.

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
