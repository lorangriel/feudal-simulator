# Feodal simulering: implementationsplan

## Mål

Förädla de strukturerade specifikationerna till beslutade, testbara krav innan
nya produktionsändringar planeras.

## Statusöversikt

- Total status: `BLOCKED`
- Senast uppdaterad: 2026-08-12
- Blocker: öppna produktfrågor i `../domains/simulation.md`.

## Prioritetsgrupper

### P0 - Beslutsunderlag

1. [OPEN] TIME-001 Besluta styrande tidsmodell
   - Beskrivning: välj år, årstid eller års-UI ovanpå säsongssteg och definiera
     snapshotfrekvens.
   - Blocker: produktbeslut saknas.
   - Kopplad specifikation: `../domains/simulation.md`.
2. [OPEN] HISTORY-001 Besluta historik- och regenereringsmodell
   - Beskrivning: definiera inkonsistens, regenerering, retention och grenar.
   - Blocker: produktbeslut saknas.
   - Kopplad specifikation: `../domains/simulation.md`.
3. [OPEN] REL-001 Besluta relationsbegrepp och UI-ansvar
   - Beskrivning: skilj personlig provinsägare från jarldömesägare och avgör
     om explicita titel-/ägarrelationer ska förbli skrivskyddade i UI.
   - Blocker: produktbeslut saknas; admin-läge ingår inte i ändringsytan.
   - Kopplad specifikation: `../status/outstanding-questions.md`.

### P1 - Avgränsa domäner

1. [BLOCKED] ECON-001 Specificera första ekonomiflödet
   - Beskrivning: ange resurser, produktion, konsumtion och acceptanskriterier.
   - Blocker: prioritering och tidsmodell är öppna.
   - Kopplad specifikation: `../domains/simulation.md`.
2. [BLOCKED] EVENT-001 Specificera första händelseflödet
   - Beskrivning: ange nivåer, urval, effekter och reproducerbarhet.
   - Blocker: omfattning och tidsmodell är öppna.
   - Kopplad specifikation: `../domains/simulation.md`.

### P2 - Implementation

1. [DEFERRED] UI-001 Inför applikationsgränsen vertikalt
   - Beskrivning: välj ett avgränsat användningsfall, definiera fråga eller
     kommando med snapshot/fel, lägg headless kontrakts- och
     applikationstester och gör Tk-flödet till en tunn adapter.
   - Blocker: första flöde och Python-kontraktsform ska beslutas; repot är i
     `SPEC` och produktionskod får inte ändras.
   - Kopplad specifikation: `../architecture/ui-boundary.md`.
2. [DEFERRED] IMPL-001 Skapa kodnära genomförandeplan
   - Beskrivning: bryt ned endast beslutade krav i små ändringar och fokuserade
     tester.
   - Blocker: P0 och relevanta P1-punkter måste vara lösta.
   - Kopplad specifikation: `../domains/simulation.md`.
3. [DEFERRED] WEB-001 Besluta om faktisk webbfrontend
   - Beskrivning: besluta funktionsomfattning, arkitektur, kontrakt och
     acceptanskriterier för en webbklient som efterliknar relevant
     Tk-funktionalitet.
   - Blocker: webbspåret är uttryckligen ett senare beslut. Den experimentella
     HTTP-listenern är inte en aktiv frontend eller förvald grund.
   - Kopplad specifikation: `../architecture/system-overview.md` och
     `../decisions/2026-08-12-client-boundaries.md`.

## Historik

- Ändringshistorik finns i `product-plan.Changelog.md`.
