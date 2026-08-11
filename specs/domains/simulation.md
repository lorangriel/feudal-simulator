# Feodal simulering: verksamhetsbeskrivning och regler

## Syfte

Simulatorn ska beskriva en feodal värld där hierarkiska förläningar och deras
lokala resurser kan granskas och förändras över tid. Tk-gränssnittet är den
primära klienten; ett enklare HTTP-gränssnitt visar samma typ av data.

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

## Bekräftade nulägesregler

1. Världen består av hierarkiska noder med lokala resurser och befolkning.
2. Noder kan ha grannar, och väder kan ge säsongsberoende mekaniska effekter.
3. Det användarstyrda tidsflödet arbetar med hela år: genomförda år låses som
   snapshots, medan planering får ske utan att äldre snapshots tas bort.
4. Tidsmotorn kan samtidigt representera årstider och använder deterministisk
   slump för reproducerbara väderutfall och snapshots.
5. Administrativ väg och personlig provinsväg har skilda ansvar; provinsvägen
   styr skatt enligt den befintliga Modell B-beskrivningen.
6. Tk-klienten erbjuder struktur-, status- och detaljpaneler. HTTP-servern är
   ett separat, enklare presentationsgränssnitt.

## Framtida inriktning från referensmaterialet

- Ekonomi med produktion, konsumtion och handel.
- Befolkningsförändring, migration och sociala relationer.
- Händelser på flera geografiska och hierarkiska nivåer.
- Förgrening eller regenerering av framtiden efter ändringar bakåt i tiden.
- Kart-, tidslinje- och förändringsvisualisering.

Dessa punkter är kandidater, inte bekräftade implementationskrav.

## Resonemang och antaganden

- Nulägesregler prioriterar observerad dokumentation och implementerade
  komponenter framför äldre visionstext.
- Skillnaden mellan årsbaserat användarflöde och säsongsbaserad intern motor
  behöver ett uttryckligt produktbeslut innan vidare tidsutveckling planeras.

## Öppna frågor

- [ ] Ska den styrande tidsenheten vara helt år, fyra årstider per år eller en
  årsbaserad UI-modell ovanpå säsongssteg?
- [ ] Vilka delar av den pensionerade ekonomivisionen är prioriterade krav?
- [ ] Ska historiska ändringar regenerera en enda framtid eller skapa grenar?
- [ ] Vilka händelser och relationer måste ingå i första kompletta simuleringen?

## Kvalitetskontroll

Senast kontrollerad: 2026-08-11

### Motsägelser

- `README.vision` anger fyra tidssteg per år, medan aktuell README beskriver
  ett användarflöde med hela år. Frågan hålls öppen ovan.

### Tvetydigheter

- Begreppet "fullständig historik" saknar ännu beslut om lagringsnivå,
  retention och eventuell förgrening.

### Otydliga beskrivningar

- Omfattningen av handel, politik, krig och allianser är inte specificerad.

### Glapp i resonemang

- Det saknas ännu mätbara acceptanskriterier för en "komplett" simulering.

## Historik

- Ändringar kommer att sparas i `simulation.Changelog.md`.
