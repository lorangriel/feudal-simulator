# Beslut: klientgränser och experimentell kod

- Datum: 2026-08-12
- Status: `ACCEPTED`

## Kontext

Repot innehåller den primära Python-/Tk-applikationen, ett C++/SDL2-spår och
en minimal HTTP-listener i Python. Förekomsten av de två senare har gjort det
otydligt vilka klienter som ingår i vår aktiva lösning. Samtidigt finns en
framtida ambition att överväga en faktisk webbfrontend som efterliknar
applikationens funktionalitet.

## Beslut

Python-/Tk-applikationen är huvudlösningen och den enda klienten i bruk.
C++/SDL2-koden under `src2/` och HTTP-listenern i `src/http_server.py` bevaras
som experimentell, ej använd kod och ingår inte i huvudlösningen.

En faktisk webbfrontend kan utvecklas senare, men funktionsomfattning,
arkitektur, teknik och prioritet kräver ett separat framtida beslut. Den
befintliga HTTP-listenern är varken en aktiv webbfrontend eller ett på förhand
valt fundament för den framtida lösningen.

## Övervägda alternativ

- Behandla samtliga tre körvägar som aktiva klienter: avvisat eftersom det
  felaktigt beskriver faktisk användning och skapar oavsiktliga
  underhållskrav.
- Göra HTTP-listenern till grund för nästa webbfrontend: inte beslutat;
  framtida behov och arkitektur ska utvärderas utan den premissen.
- Ta bort experimentkoden nu: inte valt; beslutet klassificerar ansvar och
  användning men föreskriver ingen produktionsändring i spec-läge.

## Konsekvenser

- Krav och planer ska inte räkna C++/SDL2 eller HTTP-listenern som aktiva
  produktgränssnitt.
- Experimentkoden skapar inga kompatibilitetskrav för huvudlösningen.
- Webbfrontenden ligger kvar som en uttryckligen uppskjuten fråga och får inte
  smygimplementeras genom att vidareutveckla den gamla listenern utan beslut.
- Eventuell senare borttagning eller arkivering av experimentkoden kräver en
  separat implementationsåtgärd.

## Länkar

- Arkitektur: `../architecture/system-overview.md`.
- Domän: `../domains/simulation.md`.
- Underlag: `../evidence/source-inventory.md`.
- Plan: `../plans/product-plan.md`.

## Historik

- Ändringshistorik finns i `2026-08-12-client-boundaries.Changelog.md`.
