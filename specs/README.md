# Specifikationer

Det här är repots fasta plats för levande produkt- och domänspecifikationer.
Dokumenten utgår från befintligt beteende och det tidigare visionsdokumentet,
men skiljer bekräftade nulägeskrav från framtida idéer.

## Dokument

- `domains/README.md`: karta över identifierade verksamhetsdomäner.
- `domains/simulation.md`: gemensam verksamhetsbeskrivning, begrepp och regler.
- `architecture/system-overview.md`: systemgränser och huvudkomponenter.
- `architecture/ui-boundary.md`: UI som adapter samt kontrakt för rena,
  testbara dataflöden till och från presentationen.
- `plans/product-plan.md`: prioriterade specifikations- och införandeåtgärder.
- `status/SPECSTATUS.md`: aktuell repostatus, öppna frågor och levande dokument.
- `status/outstanding-questions.md`: prioriterade kvarstående
  specifikationsfrågor från kod- och dokumentanalys.
- `decisions/`: framtida spårbara produkt- och arkitekturbeslut.
- `evidence/source-inventory.md`: underlag och härledning från tidigare material.
- `schemas/`: framtida databärande kontrakt; inga befintliga scheman ändras här.
- `prototyping/`: avgränsade POC:er som endast får skapas i bekräftat spec-läge.
- `tmp/`: temporära, icke-styrande exporter.

## Tidigare specifikationer

- `README.vision` är **retired** och bevaras som **referensmaterial**.
- Produktbeskrivningar i `README.md` är användar- och utvecklardokumentation,
  inte styrande specifikation. De har använts som nulägesunderlag.

## Arbetssätt

- Följ `.codex/skills/specifications-mode/SKILL.md`.
- Lägg domänregler, planer, beslut, underlag och arkitektur i respektive mapp.
- Lös öppna frågor innan blockerade planåtgärder flyttas till implementation.
- Ändra inte produktionskod medan repostatus är `SPEC`.

## Historik

- Ändringshistorik finns i `README.Changelog.md`.
