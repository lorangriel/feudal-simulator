# feudal-simulator
[![codecov](https://codecov.io/gh/lorangriel/feudal-simulator/branch/main/graph/badge.svg)](https://codecov.io/gh/lorangriel/feudal-simulator)

This project is a small prototype for a feudal county simulation. The code
is split across multiple modules under `src/`.

Run the Tkinter GUI application with:

```
python src/Feudal.py
```

An older shim remains for compatibility and delegates to the same entry point:

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

### Utvecklaranteckningar för huvud-UI
- Panelrubriker finns samlade i `src/ui/strings.py` och exponeras som **Struktur**, **Status** samt **Detaljer: <resurs>**. Rubriken i Detaljer-panelen uppdateras via `FeodalSimulator.update_details_header`.
- Statuspanelen beräknar en standardhöjd som rymmer minst fyra rader text vid uppstart; se `StatusPanel.calculate_heights`.
- Detaljer-panelen har en global mushjulsbindning som aktiverar scrollning även när fokus ligger på andra element.
- Alla `ttk.Combobox` använder den säkra mushjulspolicyn via `src/ui/combobox_policy.py` (patchar `ttk.Combobox` globalt så att stängda dropdowns inte byter värde).

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

## Time engine

The simulator now works with whole years only.

- **Controls**: Four toolbar buttons (−1 år, +1 år, Planering, Genomförande) plus a year dropdown. Navigation moves exactly one year at a time and can stop on uncomputed years.
- **Year statuses**: The dropdown lists years in ascending order. Green/"Låst" marks computed years, red/"Planering" marks the active year, and grey/"Ej beräknat" marks future placeholders (year 1 is always selectable).
- **Snapshots**: Each executed year becomes an immutable snapshot; planning changes never delete earlier snapshots.
- **Hooks for execution**: `TimeEngine.execute_current_year` accepts a callable that can inject future calculation logic without changing UI code.
- **Testing**: Year-based behaviour and UI hooks are covered in `tests/time/`. UI tests skip automatically when Tk is unavailable.

## Testing
Run `pytest` in the repository root to execute the automated test suite.

## Personliga provinser

- Nya fält i jarldömen: `owner_assigned_level`, `owner_assigned_id`, `personal_province_path` samt skattandelar `keep_fraction` och `tax_forward_fraction`.
- Nya nivå 1–2 fält `keep_fraction` och `tax_forward_fraction` för skatteflöden.
- Administrativ väg redovisar fortsatt befolkning och resurser medan provinsvägen styr skattflödet enligt Modell B.
- Använd hjälpfunktioner i `personal_province.py` för att validera ägande och fördela skatt.
- `pytest` kör alla domäntester inklusive de nya scenarierna.
