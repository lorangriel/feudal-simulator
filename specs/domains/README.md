# Identifierade domäner

## Syfte

Den här katalogen delar upp simulatorns verksamhetsområde i sammanhängande
domäner. Indelningen beskriver ansvar och språk; den föreskriver inte att varje
domän måste bli en egen teknisk komponent.

## Domänkarta

| Domän | Ansvar | Nuvarande mognad |
| --- | --- | --- |
| [Världsstruktur](world-structure.md) | Feodal hierarki, noder, lokala resurser, grannar och gränser | Implementerad kärna |
| [Ägande och auktoritet](ownership-and-authority.md) | Personliga provinser, skattevägar, titel–säte och jarldöme–person | Delvis implementerad |
| [Befolkning och ekonomi](population-and-economy.md) | Befolkningsgrupper, arbete, lager, licensintäkter och aggregering | Delvis implementerad |
| [Tid, väder och händelser](time-weather-and-events.md) | Planeringsår, snapshots, determinism, väder och domänhändelser | Två konkurrerande tidsmodeller |
| [Personer och hushåll](people-and-households.md) | Personregister, adelsfamilj, levnadsstandard, bostad och tjänstestab | Delvis implementerad |

`simulation.md` är den gemensamma översikten. Dokumenten ovan fördjupar
identifierade domäner utan att göra framtidsidéer till bekräftade krav.

## Samspel

1. Världsstrukturen ger identitet och administrativa vägar åt övriga domäner.
2. Ägande och auktoritet lägger alternativa personliga skattevägar samt
   explicita maktrelationer ovanpå strukturen.
3. Befolkning och ekonomi hämtar lokala bidrag från världens noder och
   sammanställer dem längs valda vägar.
4. Tid, väder och händelser anger när tillstånd får ändras, låsas och
   reproduceras.
5. Personer och hushåll tillhandahåller personer som kan bära relationer och
   hushållskrav som förbrukar ekonomiska resurser.

## Avgränsning

- Tk- och HTTP-gränssnitten är presentationskanaler, inte egna
  verksamhetsdomäner.
- JSON-lagring, adapters och UI-paneler är tekniska stödansvar.
- Kartverktyget och `src2/` är experiment och ingår inte i den bekräftade
  simuleringskärnan.
- Handel, krig, allianser och fullständig demografi är ännu kandidater till
  framtida domäner eller utökningar, inte identifierade nulägeskrav.

## Historik

- Ändringar kommer att sparas i `README.Changelog.md`.
