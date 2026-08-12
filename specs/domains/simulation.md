# Feodal simulering: verksamhetsbeskrivning och regler

## Syfte

Simulatorn ska beskriva en feodal värld där hierarkiska förläningar och deras
lokala resurser kan granskas och förändras över tid. Tk-gränssnittet i Python
är den primära och enda klienten i bruk.

## Begrepp

- **Nod**: en förläning eller lokal resurs med identitet, egenskaper och
  relationer.
- **Feodal hierarki**: föräldra-/barnrelationer från överordnade områden till
  underordnade förläningar och resurser.
- **Administrativ väg**: hierarkin som redovisar befolkning och resurser.
- **Personlig provinsväg**: ägarens provinsstruktur som styr skatteflödet.
- **Snapshot**: en beständig kopia av världstillståndet vid en tidpunkt.
- **Planeringsår**: valt år vars förändringar ännu inte har låsts genom
  genomförande.
- **Titelrelation**: uttrycklig koppling från en titel på nivå 0–2 till ett
  jarldöme på nivå 3 som fungerar som titelns säte.
- **Jarldömesägare**: uttrycklig koppling från ett jarldöme på nivå 3 till en
  person i världens globala personregister.

## Bekräftade nulägesregler

1. Världen består av hierarkiska noder med lokala resurser och befolkning.
2. Noder kan ha grannar, och väder kan ge säsongsberoende mekaniska effekter.
3. Det användarstyrda tidsflödet arbetar med hela år: genomförda år låses som
   snapshots, medan planering får ske utan att äldre snapshots tas bort.
4. Den aktiva Tk-körvägen använder `src/time/time_engine.py`: väder låses per
   helt år och genereras reproducerbart från året, med ett utfall per årstid.
   Den äldre säsongsbaserade motorn i `src/time_engine.py` är inte inkopplad i
   Tk-klienten.
5. Administrativ väg och personlig provinsväg har skilda ansvar; provinsvägen
   styr skatt enligt den befintliga Modell B-beskrivningen.
6. Tk-klienten erbjuder struktur-, status- och detaljpaneler. Den befintliga
   HTTP-listenern är ett äldre experiment som inte längre används. Även
   C++/SDL2-koden är experimentell, inte i bruk och utanför huvudlösningen.
7. Provinsläget visar ägarens ankare och bygger därefter hela trädet från
   `get_province_subtree(owner_id)` med rekursiv insert. En explicit ägare på
   en undernod bryter nedärvningen från en överordnad ägare; adminträdet har en
   separat renderingsväg och återställs när läget lämnas.
8. Sammanräkningar använder lokala bidrag för att undvika dubbelräkning:
   fysisk lagring kommer endast från `Lager`-noder, medan befolkning och arbete
   räknas enligt respektive lokala policy.
9. Titel–säte och jarldöme–ägare är separata, explicita relationer. Ett säte
   måste vara ett jarldöme i titelns administrativa delträd och får inte delas
   av flera titlar. En jarldömesägare måste finnas i personregistret; ingen av
   relationerna härleds automatiskt från den andra eller från provinsägandet.

## Framtida inriktning från referensmaterialet

- Ekonomi med produktion, konsumtion och handel.
- Befolkningsförändring, migration och sociala relationer.
- Händelser på flera geografiska och hierarkiska nivåer.
- Förgrening eller regenerering av framtiden efter ändringar bakåt i tiden.
- Kart-, tidslinje- och förändringsvisualisering.
- En faktisk webbfrontend som efterliknar relevant funktionalitet i
  applikationen. Omfattning, teknik och prioritet beslutas senare; den
  befintliga HTTP-listenern är inte den beslutade webbfrontenden.

Dessa punkter är kandidater, inte bekräftade implementationskrav.

## Resonemang och antaganden

- Nulägesregler prioriterar observerad dokumentation och implementerade
  komponenter framför äldre visionstext.
- Skillnaden mellan årsbaserat användarflöde och säsongsbaserad intern motor
  består i praktiken av två motorimplementationer och behöver ett uttryckligt
  produktbeslut innan vidare tidsutveckling planeras.

## Öppna frågor

- [ ] Ska den styrande tidsenheten vara helt år, fyra årstider per år eller en
  årsbaserad UI-modell ovanpå säsongssteg?
- [ ] Vilka delar av den pensionerade ekonomivisionen är prioriterade krav?
- [ ] Ska historiska ändringar regenerera en enda framtid eller skapa grenar?
- [ ] Vilka händelser och relationer måste ingå i första kompletta simuleringen?
- [ ] Ska de explicita titel- och ägarrelationerna förbli endast läsbara i UI,
  eller ska ett framtida icke-adminflöde få redigera dem?
- [ ] Vilken funktionalitet, arkitektur och prioritet ska en framtida faktisk
  webbfrontend få när webbspåret tas upp för beslut?

## Kvalitetskontroll

Senast kontrollerad: 2026-08-12

### Motsägelser

- `README.vision` anger fyra tidssteg per år, medan aktuell README beskriver
  ett användarflöde med hela år. Frågan hålls öppen ovan.

### Tvetydigheter

- Begreppet "fullständig historik" saknar ännu beslut om lagringsnivå,
  retention och eventuell förgrening.
- "Ägare" kan avse både personlig provinstilldelning och den separata
  relationen mellan person och jarldöme; specifikation och UI måste namnge
  vilken relation som avses.

### Otydliga beskrivningar

- Omfattningen av handel, politik, krig och allianser är inte specificerad.
- "Efterlikna applikationens funktionalitet" saknar ännu beslutad
  funktionsmängd och acceptanskriterier för en framtida webbfrontend.

### Glapp i resonemang

- Det saknas ännu mätbara acceptanskriterier för en "komplett" simulering.

## Historik

- Ändringshistorik finns i `simulation.Changelog.md`.
