# Domän: tid, väder och händelser

## Verksamhetsansvar

Domänen ordnar förändringar i simuleringsvärlden, låser historiskt tillstånd
och ger reproducerbara omvärldsutfall. Nuläget har en aktiv årsmodell och en
äldre, fristående säsongsmodell; vilken som ska vara långsiktigt styrande är
inte beslutat.

## Centrala begrepp

- **Planeringsår**: valt helt år vars tillstånd kan ändras före genomförande.
- **Låst år**: genomfört år med en snapshot.
- **Ej beräknat år**: framtida platshållare utan låst utfall.
- **Snapshot**: djup kopia av världstillståndet vid en tidsposition.
- **Årsväder**: reproducerbart utfall med ett värde per årstid inom ett år.
- **Domänhändelse**: meddelande om ett inträffat domänfaktum, exempelvis
  ändrad personlig provinsägare.

## Bekräftade regler för aktiv Tk-körväg

1. Användaren navigerar i hela år och kan inte gå före år 1.
2. Planeringsändringar lagras per valt år och får inte radera äldre låsta år.
3. Genomförande kopierar planeringstillståndet, kör en valfri
   beräkningsfunktion, låser resultatet och öppnar nästa planeringsår.
4. Utlämnade snapshots är kopior; anroparen ska inte kunna mutera motorns
   interna historik genom dem.
5. Väder låses deterministiskt från året och ger vår-, sommar-, höst- och
   vinterutfall även om användarens styrande tidssteg är ett helt år.

## Separat äldre modell

`src/time_engine.py` går i årstider, sparar komprimerade snapshots med
checksumma och tidslinje-id samt kan markera och trunkera en smutsig framtid.
Den importeras inte av den aktiva Tk-klienten. Dess beteende är därför underlag
för ett framtida beslut, inte bindande nulägeskrav.

## Domängränser

- Domänen styr ordning, reproducerbarhet och historik, men varje annan domän
  äger sina egna beräkningsregler.
- Händelsebussen distribuerar fakta och ska inte vara den auktoritativa
  lagringen av världstillstånd.
- Väderutfall finns, men effekter på ekonomi och befolkning kräver separata
  domänregler.

## Kvalitetskontroll

- **Motsägelse:** referensvisionens fyra styrande tidssteg per år skiljer sig
  från den aktiva årsmodellen.
- **Glapp:** retention, regenerering efter historisk ändring och eventuella
  förgrenade tidslinjer saknar produktbeslut.
- **Otydlighet:** vilka domänberäkningar som måste ske vid genomförande av ett
  år är ännu inte definierat.

## Historik

- Ändringar kommer att sparas i `time-weather-and-events.Changelog.md`.
