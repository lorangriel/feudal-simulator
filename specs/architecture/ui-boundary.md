# UI-gräns och applikationskontrakt

## Syfte

Användargränssnittet är en utbytbar presentationsadapter till simuleringen.
Det är inte en egen verksamhetsdomän: Tk, en framtida webbklient och testkod
ska använda samma applikationsgräns utan att domänregler flyttas in i en viss
presentationsteknik.

Detta dokument anger målarkitekturen. Nuvarande Tk-kod får migreras stegvis;
att den i dag anropar domänobjekt och delar muterbara datastrukturer direkt
gör inte kopplingen till ett godkänt kontrakt.

## Ansvarsgränser

### Presentation

UI-adaptern ansvarar för widgetar, layout, navigering, lokalt visningstillstånd,
inmatningsinsamling, formatering och översättning av ett svar till en vy. Den
får validera presentationsdetaljer, exempelvis att ett obligatoriskt fält inte
är tomt, men äger inga simuleringsregler.

### Applikationsgräns

Applikationslagret exponerar användningsfall som teknikneutrala frågor och
kommandon. Det samordnar domäntjänster, transaktioner och beständighet samt
översätter domänresultat till kontraktsdata. Det är den enda ordinarie vägen
för en UI-adapter att läsa eller ändra simuleringen.

### Domän och infrastruktur

Domänen äger regler, beräkningar och invariants. Infrastruktur äger bland
annat filåtkomst och beständighet bakom portar som applikationslagret använder.
Inget av lagren får importera Tk eller känna till widgetar, dialoger eller
presentationshändelser.

## Dataflöden

### Läsning

1. UI:t skickar en fråga med enkla kontraktsvärden, exempelvis ett nod-id.
2. Applikationslagret läser och beräknar via domänen.
3. UI:t får en frikopplad, skrivskyddad snapshot/DTO av de fält som
   användningsfallet behöver.
4. UI:t renderar svaret utan att behålla en muterbar referens till
   domänmodellen.

### Ändring

1. UI:t skapar ett uttryckligt kommando av användarens avsikt.
2. Applikationslagret validerar behörigt användningsfall och låter domänen
   upprätthålla reglerna.
3. Resultatet är ett uttryckligt lyckat svar eller ett teknikneutralt fel med
   stabil kod och relevanta fältdetaljer.
4. UI:t väljer hur resultatet presenteras och begär vid behov en ny snapshot.

UI:t får inte mutera delade världs-dictionaries, anropa sparning som en
biverkan av rendering eller använda Tk-callbackar som applikationskontrakt.

## Kontraktsregler

- Gränsen består av namngivna frågor, kommandon, svar och fel; den exponerar
  inte `tkinter`-typer, widgetar eller UI-klasser.
- Kontraktsdata innehåller endast serialiserbara värden, stabila identifierare
  och uttryckligt definierade sammansättningar. Domänobjekt och levande
  muterbara samlingar lämnas inte till klienten.
- Varje kommando beskriver en användaravsikt, inte en widgethändelse. Exempel:
  `AdvanceTime` är tillåtet medan `OnNextButtonClick` inte är det.
- Frågor saknar domänmutation. Kommandon får inte kräva att klienten först
  ändrar intern världsdata.
- Domän- och applikationsfel översätts vid gränsen. Dialogtext och annan
  presentationstext tillhör UI-adaptern.
- Kontrakt ska kunna versionshanteras eller utökas additivt när fler klienter
  tillkommer. Interna Python-klasser är inte automatiskt publika kontrakt.
- Samma kontrakt ska kunna anropas synkront in-process av Tk och senare
  placeras bakom en transportadapter utan att domänens användningsfall skrivs
  om. Ingen nätverkstransport beslutas här.

## Beroenderiktning

`Tk-adapter -> applikationsport -> domän`

Beständighet och andra tekniska integrationer implementerar portar riktade
inåt. En framtida UI-implementation ersätter eller kompletterar Tk-adaptern;
den får inte skapa en parallell uppsättning domänregler.

## Testbarhetskrav

- Applikationsfrågor och kommandon ska kunna testas utan Tk-root, display eller
  en körande eventloop.
- Kontraktstester ska verifiera indata, svar, felkoder och att snapshots inte
  ger klienten en mutationsväg tillbaka till domäntillståndet.
- Domänregler testas under applikationsgränsen och UI-adaptern testas separat
  med testdubblar för porten.
- En ny UI-adapter ska kunna återanvända samma kontraktstester. Endast
  adaptertester ska vara teknikberoende.
- Ett användningsfall räknas inte som frikopplat förrän dess Tk-kod saknar
  direkt åtkomst till muterbar världsdata och domänens konkreta managers.

## Migreringsprincip

Gränsen införs vertikalt, ett användningsfall i taget. För varje flöde
identifierar vi först fråga/kommando och svar, lägger kontrakts- och
applikationstester under gränsen och flyttar därefter Tk-koden till en tunn
adapter. En stor omskrivning av hela UI:t är varken nödvändig eller önskad.

Exakta första användningsfall och kontraktsformer beslutas före implementation.
JRDL eller annat transportformat behövs först när vi vill göra kontraktet
språk- eller processöverskridande; Python-typer kan räcka för den första
in-process-gränsen.

## Kopplade dokument

- Beslut: `../decisions/2026-08-12-ui-as-adapter.md`.
- Systemöversikt: `system-overview.md`.
- Klientgränser: `../decisions/2026-08-12-client-boundaries.md`.
- Plan: `../plans/product-plan.md`.

## Historik

- Ändringshistorik finns i `ui-boundary.Changelog.md`.
