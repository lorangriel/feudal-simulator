# Changelog: Specifications Mode skill

- 2026-07-15: Lade till direktiv om att changelog-filer ska vara omvänt kronologiska med nya poster överst.
- 2026-07-13: Lade till arbetsflödet "Refresh specifications" för synkronisering av specs, git-historik vid oklarheter, omprövning av implementationplaner och destillering av utestående specifikationsfrågor.
- 2026-07-09: Förtydligade att varje POC ska dokumentera hur erfarenheter återkopplas till beslut, hypotes-/planverifiering, levande specifikationer och samlingsöversikten.
- 2026-07-08: Lade till policyn för separata `document.Changelog.md`-filer och regeln att changelog-filer inte ska läsas by default.
- 2026-07-08: Lade till spec-lägesprototyping som avgränsat beslutsunderlag under `specs/prototyping/<poc-name>/`, med Python som rekommenderat POC-verktyg.
- 2026-07-08: Förtydligade att POC:er i spec-läge ska ha verifierande testfall och regressionstester.
- 2026-07-08: Lade till obligatorisk historikhänvisning sist i primärdokumentet.
- 2026-07-08: Förtydligade att rekommenderade POC:er ska vara implementerbara under en session, sammanfattas i samlings-README och inte läsas by default.
- 2026-07-08: Lade till att `.jrdl`-kontrakt kan användas för POC-kodgenerering via Alpha `jrdl2python` eller `jrdl2openrpc` och `openrpc-generator`, men att genererad kod inte ska checkas in.
- 2026-07-08: Kompletterade skillen med en självbärande sammanfattning av JRDL-syntaxen från Alpha-specifikationen.
- 2026-07-08: Uppdaterade JRDL-syntaxbeskrivningen: integer enumeration value documentation är vanlig metadata och ska inte beskrivas som reserverad för C-konstantnamn.
- 2026-07-08: Återställde changelog-regeln till radformatet `- <YYYY-MM-DD>: <kommentar>` och förbjöd datumrubriker i changelog-filer.
