# Domän: personer och hushåll

## Verksamhetsansvar

Domänen beskriver identifierbara personer och den nuvarande modellen för ett
adligt hushålls sammansättning, levnadsstandard, bostad och tjänstebehov.
Den omfattar ännu inte en generell livscykel- eller relationssimulering.

## Centrala begrepp

- **Personregister**: världens globala uppslag av personer efter identitet.
- **Adelsfamilj**: länsherre, makar, barn och släktingar knutna till en nod.
- **Platshållare**: namngiven hushållsmedlem utan fullständig personpost.
- **Levnadsstandard**: ordinal nivå från Enkel till Furstlig.
- **Bostadskrav**: lägsta byggnadstyp som stödjer en levnadsstandard.
- **Tjänstestab**: beräknat antal roller för ett hushåll vid en viss
  levnadsnivå.

## Bekräftade regler

1. En hushållsmedlem räknas om posten är en giltig personreferens, en namngiven
   platshållare eller ett bakåtkompatibelt enkelt värde.
2. Hushållets storlek är summan av länsherre, makar, barn och släktingar.
3. Levnadsstandarderna har en fast ordning och mappar till levnadsnivå samt
   bostadstyp.
4. Högsta tillåtna standard begränsas av den högst rankade tillgängliga
   bostadsbyggnaden.
5. Tjänstebehov och kostnad beräknas från levnadsnivå och antal adliga
   hushållsmedlemmar enligt rollspecifika tabeller.
6. En explicit jarldömesägare måste referera en person i det globala
   registret; en lokal karaktärsresurs är inte automatiskt samma relation.

## Domängränser

- Ägande och auktoritet äger relationen mellan person och jarldöme.
- Befolkning och ekonomi äger aggregerade befolkningsgrupper och ekonomiska
  resurser; hushållet beskriver specifika personer och deras krav.
- Byggnader ligger lokalt i världsstrukturen men tolkas här som stöd för
  levnadsstandard.

## Kvalitetskontroll

- **Tvetydighet:** globala personer, lokala `characters`-poster,
  `ruler_id` och hushållsplatshållare bildar ännu ingen enhetlig personmodell.
- **Glapp:** födelse, död, ålder, släktskap, succession och relationers
  förändring över tid saknar bekräftade regler.
- **Otydlighet:** tjänstekostnadernas enhet och koppling till lager eller
  årsbudget är inte specificerad.

## Historik

- Ändringar kommer att sparas i `people-and-households.Changelog.md`.
