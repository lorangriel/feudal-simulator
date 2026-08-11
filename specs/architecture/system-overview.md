# Systemöversikt: arkitektur

## Syfte och omfattning

Dokumentet beskriver nuvarande huvudgränser utan att föreskriva ändringar i
server, datakontrakt, `world_manager` eller admin-läge.

## Systemgränser och komponenter

- `src/Feudal.py` startar Tk-applikationen.
- UI- och presentationsmoduler under `src/` visar struktur, status, detaljer
  och kartvyer.
- Domänmoduler hanterar noder, resurser, befolkning, personliga provinser,
  väder och relationer.
- `src/time_engine.py` ansvarar för tidspositioner, deterministisk slump,
  snapshots och beständig tidslinjedata.
- `src/http_server.py` erbjuder en minimal HTML-presentation vid sidan av
  Tk-klienten.
- `src2/` är ett separat experiment i C++/SDL2 och ingår inte i den primära
  Python-applikationens körväg.

## Gränssnitt och dataflöden

Världsdata läses in i domänobjekt och presenteras av klienterna. UI-kommandon
ändrar planering eller driver tidsmotorn, som skapar snapshots och händelser.
Personlig provinslogik kompletterar den administrativa nodhierarkin för
ägande- och skatteflöden.

## Kvalitetsattribut och constraints

- Simuleringsutfall ska kunna reproduceras med deterministisk slump.
- Tidigare snapshots ska vara oföränderliga ur användarflödets perspektiv.
- Domänlogik ska kunna testas utan ett grafiskt fönster; UI-test ska kunna
  hoppas över i headless-miljö.
- Admin-läge och den administrativa hierarkin får inte påverkas oavsiktligt av
  provinslägets presentationsväg.

## Kopplade beslut och underlag

- Beslut: inga formella beslutsposter ännu.
- Underlag: `../evidence/source-inventory.md`.
- Domänregler: `../domains/simulation.md`.

## Historik

- Ändringar kommer att sparas i `system-overview.Changelog.md`.
