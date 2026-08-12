# Systemöversikt: arkitektur

## Syfte och omfattning

Dokumentet beskriver nuvarande huvudgränser utan att föreskriva ändringar i
datakontrakt, `world_manager` eller admin-läge. Den primära lösningen är
Python-/Tk-applikationen.

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
- `src/http_server.py` är en bevarad experimentell HTTP-presentation. Den är
  inte längre i bruk och ingår inte i den primära lösningens körväg.
- `src2/` är ett bevarat experiment i C++/SDL2. Det är inte i bruk och ingår
  inte i den primära Python-lösningen.
- En framtida faktisk webbfrontend är en möjlig separat klient, men dess
  omfattning, teknik och gränssnitt är ännu inte beslutade. Den befintliga
  HTTP-listenern ska inte betraktas som dess grund eller som aktiv frontend.

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
- Experimenten i `src/http_server.py` och `src2/` får inte behandlas som
  produktionsberoenden eller begränsa utformningen av en framtida webbklient.

## Kopplade beslut och underlag

- Beslut: `../decisions/2026-08-12-client-boundaries.md`.
- Underlag: `../evidence/source-inventory.md`.
- Domänregler: `../domains/simulation.md`.

## Historik

- Ändringshistorik finns i `system-overview.Changelog.md`.
