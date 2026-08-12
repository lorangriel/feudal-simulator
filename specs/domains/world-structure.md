# Domän: världsstruktur

## Verksamhetsansvar

Domänen beskriver den feodala världens rumsliga och administrativa stomme.
Den avgör vilka objekt som finns, hur de är underordnade varandra och vilka
lokala egenskaper som kan sammanställas av andra domäner.

## Centrala begrepp

- **Värld**: en samling noder, personer och explicita relationstabeller.
- **Nod**: identifierbart objekt med en valfri förälder, barn och lokala data.
- **Djup**: nodens nivå i föräldrahierarkin; nivå 0–2 representerar titlar och
  nivå 3 ett jarldöme i de explicita relationsreglerna.
- **Resursnod**: undernod som bär ett lokalt bidrag, exempelvis lager,
  befolkning, mark, byggnad, djur eller väder.
- **Granne**: högst en koppling i vardera av nodens sex grannplatser.
- **Gränstyp**: egenskap på en grannkoppling, exempelvis väg, berg eller
  vattendrag.

## Bekräftade regler

1. Nodidentiteter ska kunna normaliseras från heltal eller numeriska strängar.
2. Föräldra-/barnrelationen definierar den administrativa hierarkin och får
   inte antas vara samma sak som en personlig provinsväg.
3. Traversering måste skydda mot cykler och saknade noder; ogiltig härkomst
   får inte användas för att härleda giltiga titel- eller ägarrelationer.
4. En nod har högst sex normaliserade grannplatser. En grannrelation och dess
   gränstyp ska hållas konsekvent mellan båda noderna när de redigeras.
5. Radering av en nod omfattar dess administrativa efterkommande.
6. Resurstypen avgör vilka lokala fält som har verksamhetsbetydelse. Exempelvis
   kommer fysisk lagring endast från noder av typen `Lager`.

## Domängränser

- Domänen äger struktur och lokal placering, men inte reglerna för
  skattefördelning eller personrelationer.
- Summeringsregler definieras i befolknings- och ekonomidomänen.
- Titel–säte använder strukturen för validering men ägs av domänen ägande och
  auktoritet.

## Kvalitetskontroll

- **Tvetydighet:** nivåernas fullständiga verksamhetsnamn och tillåtna antal
  nivåer är inte samlat specificerade.
- **Glapp:** regler för flytt av en hel delhierarki och följdeffekter på
  grannar, säten och personliga vägar saknas.
- **Motsägelse:** ingen direkt motsägelse identifierad i nulägesunderlaget.

## Historik

- Ändringar kommer att sparas i `world-structure.Changelog.md`.
