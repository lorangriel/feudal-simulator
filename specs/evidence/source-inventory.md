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
- `src/feodal_simulator.py`, `src/time/time_engine.py` och
  `src/time/weather_lock.py` (lästa 2026-08-11): bekräftar att Tk-körvägen är
  årsbaserad, bevarar låsta snapshots och låser reproducerbart årsväder.
- `src/time_engine.py` (läst 2026-08-11): innehåller en separat säsongsbaserad
  motor med beständig lagring, men saknar import från Tk-körvägen.
- `src/personal_province.py`, `src/ui/views/structure_view.py` och relevanta
  domän-/UI-tester (lästa 2026-08-11): bekräftar ägararv, avbrott vid explicit
  underägare och att provinsrendering utgår från `get_province_subtree`.
- `src/rollup_policy.py`, `src/world_relations.py` och deras tester (lästa
  2026-08-11): bekräftar lokala bidragspolicyer samt explicita, validerade
  titel–säte- och jarldöme–ägare-relationer.

## Tolkning och begränsningar

Inventeringen är en riktad kodanalys, inte en fullständig rad-för-rad-revision.
Visionens framtidsidéer har inte automatiskt gjorts till krav. Nya beslut ska
spåras i `specs/decisions/` i stället för att skrivas tillbaka till visionen.

## Stödjer

- Krav: `../domains/simulation.md`.
- Arkitektur: `../architecture/system-overview.md`.
- Plan: `../plans/product-plan.md`.

## Historik

- Ändringshistorik finns i `source-inventory.Changelog.md`.
