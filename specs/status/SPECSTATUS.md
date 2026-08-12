# Specifikationsstatus

- Sticky specmapp: `specs/`
- Repostatus: `SPEC`
- Uppstartsnivå: `STRUCTURED`
- Senast uppdaterad: 2026-08-12

## Levande dokument

- `specs/domains/README.md`: domänkarta med fem identifierade domäner.
- `specs/domains/simulation.md`: gemensamma domänregler och öppna frågor.
- `specs/domains/*.md`: fördjupningar av världsstruktur, ägande och auktoritet,
  befolkning och ekonomi, tid/väder/händelser samt personer och hushåll.
- `specs/architecture/system-overview.md`: arkitekturöversikt, första utgåva.
- `specs/architecture/ui-boundary.md`: beslutad målgräns mellan utbytbar UI-
  adapter, applikationsanvändningsfall och domän.
- `specs/evidence/source-inventory.md`: källunderlag, första utgåva.
- `specs/plans/product-plan.md`: implementationsplan, blockerad av öppna frågor.
- `specs/status/outstanding-questions.md`: prioriterade kvarstående
  specifikationsfrågor efter kodanalys.

## Öppna frågor

- Styrande tidsenhet och snapshotfrekvens.
- Historisk regenerering kontra förgrenade tidslinjer.
- Prioritering och avgränsning av ekonomi, händelser och relationer.
- UI-ansvar och terminologi för explicita titel-/ägarrelationer jämfört med
  personlig provinstilldelning.
- Senare avgränsning och arkitektur för en faktisk webbfrontend.
- Första användningsfall och exakt Python-kontraktsform för UI-migreringen.

## Fastställda klientgränser

- Python/Tk är huvudlösningen och den enda klienten i bruk.
- Befintlig HTTP-listener och C++/SDL2-kod är bevarade experiment utanför
  huvudlösningen; se `../decisions/2026-08-12-client-boundaries.md`.
- UI är en presentationsadapter, inte en verksamhetsdomän. Tk ska stegvis
  flyttas bakom en teknikneutral och headless-testbar applikationsport; se
  `../decisions/2026-08-12-ui-as-adapter.md`.

## MCP-stöd

- Tillgängligt: nej; inga projektspecifika MCP-resurser identifierades.
- Källa för prioritering/åtgärder/status: repots dokument och kodöversikt.

## Väntar på bekräftelse

- Föreslaget byte: inget.
- Fråga ställd: nej; användaren begärde uttryckligen att motsvarande
  specifikationer skulle skapas.

## Historik

- Ändringshistorik finns i `SPECSTATUS.Changelog.md`.
