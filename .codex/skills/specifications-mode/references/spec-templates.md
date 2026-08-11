# Specifications Mode Templates

## Verksamhetsbeskrivning och regler

```md
# <Topic>: Verksamhetsbeskrivning och regler

## Syfte
- <Why this domain/rule set exists.>

## Begrepp
- **<Term>**: <Definition.>

## Regler
1. <Rule.>
2. <Rule.>

## Resonemang och antaganden
- <Assumption or rationale.>

## Öppna frågor
- [ ] <Question.>

## Kvalitetskontroll
Senast kontrollerad: <YYYY-MM-DD>

### Motsägelser
- <None found / finding.>

### Tvetydigheter
- <None found / finding.>

### Otydliga beskrivningar
- <None found / finding.>

### Glapp i resonemang
- <None found / finding.>

```

## Implementationsplan

Skapa eller underhåll normalt inte en implementationsplan när öppna frågor, öppna beslut, motsägelser, tvetydigheter, otydliga beskrivningar eller resonemangsglapp fortfarande behöver lösas. Om brukaren uttryckligen begär planuppdatering ändå, synliggör dessa punkter som blockers eller risker.

```md
# <Topic>: Implementationsplan

## Mål
- <Target outcome.>

## Statusöversikt
- Total status: <OPEN | IN_PROGRESS | RESOLVED | BLOCKED | DEFERRED>
- Senast uppdaterad: <YYYY-MM-DD>

## Prioritetsgrupper

### P0 - <Name>
1. [OPEN] <Action id/title>
   - Beskrivning: <Action details.>
   - Blocker: <None / blocker.>
   - Kopplad specifikation: <Link or path.>

### P1 - <Name>
1. [OPEN] <Action id/title>
   - Beskrivning: <Action details.>
   - Blocker: <None / blocker.>
   - Kopplad specifikation: <Link or path.>

```

## Sticky spec folder README

```md
# Specifikationer

Den här mappen är repots sticky plats för specifikationer. Fortsätt använda den för verksamhetsbeskrivningar, regler, implementationsplaner och specstatus.

## Dokument
- `domains/`: verksamhetsbeskrivningar och regler per domänområde.
- `plans/`: implementationsplaner, prioriteringar, åtgärder och status.
- `decisions/`: beslut med valt alternativ, kontext, alternativ, konsekvenser och länkat underlag.
- `evidence/`: underlag, källor, observationer, experiment och fakta som stödjer krav eller beslut.
- `architecture/`: arkitektur, systemgränser, komponentrelationer, gränssnitt och kvalitetsattribut.
- `schemas/`: databärande kontrakt som stödjer specifikationsarbete, till exempel JRDL-schema med rena JRDL-typer, XML-schema, JSON-schema eller andra explicita kontraktsformat.
- `status/SPECSTATUS.md`: aktuell specstatus och levande dokument.
- `prototyping/`: avgränsade POC-mappar som bara används i spec-läge för att lösa frågor eller skapa beslutsunderlag; samlings-README listar POC:er med status `OPEN` eller `FINISHED`.
- `tmp/`: temporära, genererade exportdokument utan styrande funktion, till exempel öppna frågor i `.tex`.

## Introduktionsnivå
- `NONE`: föreslå källkodsscanning för preliminära verksamhetsbeskrivningar.
- `UNSTRUCTURED`: föreslå strukturering av befintliga dokument.
- `STRUCTURED`: fortsätt underhålla levande dokument.

## Principer
- Specifikationer gäller produktens/problemets domän, inte mekaniska handgrepp som skill-författande.
- Använd undermappar för tydliga domänområden.
- Håll dokumentationen tillräckligt kort för att spara agent-bränsle.
- Bevara tydlighet, beslut och status även när text komprimeras.
- Rekommendera prototyping när ett litet experiment kan ge snabb vägledning för fortsatt specifikationsarbete.
```
## Schema / databärande kontrakt

Använd för kontrakt som specificerar dataform, validering och dokumentationsmetadata. Håll domänresonemang i `domains/`, beslut i `decisions/` och arkitekturkonsekvenser i `architecture/`.

````md
# <Topic>: Schema

## Syfte
- <Vilket kontrakt schemat definierar och vilka specifikationer det stödjer.>

## Format
- Typ: <JRDL | XML Schema | JSON Schema | other>
- Fil(er): <Path(s) to schema files or embedded contract.>

## Kontraktsregler
- <Rule about allowed types, documentation metadata, validation, versioning, etc.>

## Schema
```<format>
<Schema excerpt or full schema if it is concise enough.>
```

## Stödjer
- Domänspecifikationer: <Path/link or none.>
- Beslut: <Path/link or none.>
- Planer: <Path/link or none.>

````

## Spec-läge status

```md
# Specifikationsstatus

- Sticky specmapp: `specs/`
- Repostatus: <NON_SPEC | SPEC_PROPOSED | SPEC | IMPLEMENTATION_PROPOSED | IMPLEMENTATION>
- Uppstartsnivå: <NONE | UNSTRUCTURED | STRUCTURED>
- Senast uppdaterad: <YYYY-MM-DD>

## Levande dokument
- `<path>`: <type>, <current status>, <notes.>

## MCP-stöd
- Tillgängligt: <yes | no | unknown>
- Källa för prioritering/åtgärder/status: <resource/tool or none>


## Väntar på bekräftelse
- Föreslaget byte: <none | current -> target>
- Fråga ställd: <yes | no>

```


## Beslut (Decision record)

```md
# <Topic>: Beslut

- Datum: <YYYY-MM-DD>
- Status: <PROPOSED | ACCEPTED | SUPERSEDED | REJECTED>
- Beslut: <Chosen option.>

## Kontext
- <Problem, constraints, and why a decision is needed.>

## Alternativ
1. <Option and tradeoff.>
2. <Option and tradeoff.>

## Konsekvenser
- Positivt: <Expected benefit.>
- Negativt/risk: <Known cost or risk.>

## Underlag
- <Path/link to evidence.>

## Påverkar
- Planer: <Path/link or none.>
- Arkitektur: <Path/link or none.>

```

## Underlag (Evidence)

```md
# <Topic>: Underlag

## Syfte
- <What question this evidence helps answer.>

## Källor och observationer
- <Source/observation/experiment and date.>

## Tolkning och begränsningar
- <What can and cannot be concluded.>

## Stödjer
- Krav: <Path/link or none.>
- Beslut: <Path/link or none.>

```

## Arkitektur

```md
# <Topic>: Arkitektur

## Syfte och omfattning
- <Architecture area and boundaries.>

## Systemgränser och komponenter
- <Components, responsibilities, and relationships.>

## Gränssnitt och dataflöden
- <Interfaces, contracts, or flows.>

## Kvalitetsattribut och constraints
- <Performance, determinism, maintainability, portability, etc.>

## Kopplade beslut och underlag
- Beslut: <Path/link or none.>
- Underlag: <Path/link or none.>

```


## Prototyping samlings-README

```md
## POC:er
Statusvärden: `OPEN`, `FINISHED`.

| POC | Status | Fråga | Senaste resultat |
| --- | --- | --- | --- |
| `<poc-name>/` | OPEN | <question> | <short result or pending> |
```

## Prototyping-POC

Skapa en egen undermapp under `specs/prototyping/<poc-name>/` för varje POC. En rekommenderad POC ska vara så liten att den kan implementeras under en session. Python rekommenderas, men välj fritt verktyg när frågan tjänar på det. Varje POC ska ha verifierande testfall och regressionstester som kan köras om. Sammanfatta POC:en i `specs/prototyping/README.md` med status `OPEN` eller `FINISHED`.

```md
# <POC name>

## Fråga
- <Vilken utestående fråga eller vilket beslut POC:en ska stödja.>

## Hypotes / alternativ
- <Vad vi testar eller jämför.>

## Körning
- Kommando: `<command>`
- Beroenden: <none / dependencies>

## Verifierande testfall och regression
- Testkommando: `<test command>`
- Förväntat resultat: <expected result>
- Regressionstäckning: <Vilket beteende/resultat testet låser.>

## Resultat
- <Kort observation.>

## Rekommendation
- <Hur resultatet bör påverka specifikationen eller beslutet.>
```


## Obligatorisk historikhänvisning sist i varje spec-dokument

Lägg sist i primära spec-dokument. Om changelog-filen finns, använd första raden. Om filen ännu saknas, använd andra raden tills filen skapas.

```md
## Historik
- Ändringshistorik finns i `<Document name>.Changelog.md`.
```

```md
## Historik
- Ändringar kommer att sparas i `<Document name>.Changelog.md`.
```


## Separat historikfil

Skapa bara när historik behövs för motsvarande Markdown-dokument. Läs inte dessa filer by default; använd dem vid historikutredning, statusrekonstruktion eller explicit fråga om historik.

```md
# <Document title>: historik

- <YYYY-MM-DD>: <Change.>
```


## Temporär `.tex`-export av öppna frågor

```tex
\documentclass[a4paper,11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[swedish]{babel}
\usepackage[a4paper,margin=28mm]{geometry}
\title{Temporär export: öppna frågor}
\date{<YYYY-MM-DD>}
\begin{document}
\maketitle
\textbf{Detta dokument är genererat, temporärt och flyktigt. Det är inte styrande och ersätter inte källdokumenten under specs/.}

\section*{Källor}
\begin{itemize}
  \item <specs/status/SPECSTATUS.md eller annat källdokument>
\end{itemize}

\section*{Öppna frågor och beslut}
\begin{itemize}
  \item <Fråga/beslut som behöver lösas, med källdokument.>
\end{itemize}
\end{document}
```

## Historik
- Ändringshistorik finns i `spec-templates.Changelog.md`.
