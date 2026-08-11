# Källinventering: underlag

## Syfte

Inventeringen anger vilket befintligt material som användes för den första
strukturerade specifikationsuppsättningen.

## Källor och observationer

- `README.md` (läst 2026-08-11): beskriver körvägar, nuvarande UI, hela år,
  snapshots, testning och personliga provinser.
- `README.vision` (läst 2026-08-11): äldre vision om hierarki, ekonomi,
  händelser, fyra tidssteg per år och historik. Dokumentet är nu retired och
  endast referensmaterial.
- `src/node.py`, `src/time_engine.py`, `src/events.py` och `src/weather.py`
  (översiktligt lästa 2026-08-11): bekräftar centrala nod-, tids-, händelse-
  och väderbegrepp.

## Tolkning och begränsningar

Inventeringen är en inledande källöversikt, inte en fullständig kodrevision.
Visionens framtidsidéer har inte automatiskt gjorts till krav. Nya beslut ska
spåras i `specs/decisions/` i stället för att skrivas tillbaka till visionen.

## Stödjer

- Krav: `../domains/simulation.md`.
- Arkitektur: `../architecture/system-overview.md`.
- Plan: `../plans/product-plan.md`.

## Historik

- Ändringar kommer att sparas i `source-inventory.Changelog.md`.
