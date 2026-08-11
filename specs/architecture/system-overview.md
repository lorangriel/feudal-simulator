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
- `src/time/time_engine.py` är Tk-klientens aktiva årsbaserade tidsmotor och
  `src/time/weather_lock.py` låser deterministiskt väder per år. Den separata
  `src/time_engine.py` implementerar en äldre säsongsbaserad och beständig
  tidslinje men importeras inte av Tk-körvägen.
- `src/rollup_policy.py` avgränsar vilka lokala värden som får bidra till
  rekursiva rapporter; `WorldManager` utför traverseringen.
- `src/world_relations.py` är en domänadapter för validering samt atomära läs-
  och skrivoperationer för titel–säte och jarldöme–ägare. Detaljvyn använder
  en separat presentationsadapter och visar relationerna skrivskyddat.
- `src/http_server.py` erbjuder en minimal HTML-presentation vid sidan av
  Tk-klienten.
- `src2/` är ett separat experiment i C++/SDL2 och ingår inte i den primära
  Python-applikationens körväg.

## Gränssnitt och dataflöden

Världsdata läses in i domänobjekt och presenteras av klienterna. UI-kommandon
ändrar planering eller driver tidsmotorn, som skapar snapshots och händelser.
Personlig provinslogik kompletterar den administrativa nodhierarkin för
ägande- och skatteflöden. Provinsvyn hämtar sitt träd via
`get_province_subtree(owner_id)` och renderar svaret rekursivt under ett
ägarankare; adminvyn byggs och återställs separat.

## Kvalitetsattribut och constraints

- Simuleringsutfall ska kunna reproduceras med deterministisk slump.
- Tidigare snapshots ska vara oföränderliga ur användarflödets perspektiv.
- Domänlogik ska kunna testas utan ett grafiskt fönster; UI-test ska kunna
  hoppas över i headless-miljö.
- Admin-läge och den administrativa hierarkin får inte påverkas oavsiktligt av
  provinslägets presentationsväg.
- Rapportvärden ska räknas från lokala bidrag så att redan aggregerade värden
  inte dubbelräknas vid rekursiv traversering.
- Relationer ska valideras utan mutation; skrivoperationer får mutera först
  när hela den begärda relationen är giltig.

## Kopplade beslut och underlag

- Beslut: inga formella beslutsposter ännu.
- Underlag: `../evidence/source-inventory.md`.
- Domänregler: `../domains/simulation.md`.

## Historik

- Ändringshistorik finns i `system-overview.Changelog.md`.
