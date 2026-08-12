# Beslut: UI som presentationsadapter

- Datum: 2026-08-12
- Status: `ACCEPTED`

## Kontext

Tk-applikationen är vår enda aktiva klient, men delar av presentationen har
direkt åtkomst till konkreta managers och muterbar världsdata. Det försvårar
headless-testning och gör ett framtida byte av presentationsteknik dyrt.

Att kalla UI:t en egen verksamhetsdomän skulle samtidigt blanda teknisk
presentation med simuleringens verksamhetsbegrepp. Behovet är i stället en
tydlig arkitekturgräns runt användningsfallen.

## Beslut

UI behandlas som en separat presentationsadapter, inte som en
verksamhetsdomän. Tk och möjliga framtida klienter ska bero på en
teknikneutral applikationsport med uttryckliga frågor, kommandon, snapshots
och fel. Domän- och infrastrukturlager får inte bero på UI-teknik.

Gränsen införs stegvis per användningsfall och specificeras i
`../architecture/ui-boundary.md`.

## Övervägda alternativ

- **UI som egen verksamhetsdomän:** avvisat eftersom widgetar, navigering och
  presentation inte utgör simuleringens verksamhetsregler.
- **Fortsatt direkt Tk–domänkoppling:** avvisat eftersom delad muterbar data
  och konkreta managers ger svårisolerade tester och klientinlåsning.
- **Nätverks-API som obligatorisk gräns:** avvisat nu; en in-process-port ger
  separation utan distributionskomplexitet och kan senare transportanpassas.
- **Full omskrivning före fortsatt arbete:** avvisat till förmån för vertikal,
  testdriven migrering av ett användningsfall i taget.

## Konsekvenser

- Nya UI-flöden ska inte introducera direkt mutation av världsdata.
- Applikationskontrakt och domänbeteende kan testas headless; Tk testas som en
  separat adapter.
- Ett framtida UI-byte återanvänder användningsfallen men kräver en ny adapter.
- Nuvarande kopplingar är migreringsskuld, inte prejudikat för nya kontrakt.
- Första migreringsflöde och exakt Python-kontraktsform återstår att välja.

## Länkar

- Arkitektur: `../architecture/ui-boundary.md`.
- Systemöversikt: `../architecture/system-overview.md`.
- Plan: `../plans/product-plan.md`.
- Status: `../status/outstanding-questions.md`.

## Historik

- Ändringshistorik finns i `2026-08-12-ui-as-adapter.Changelog.md`.
