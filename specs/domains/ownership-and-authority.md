# Domän: ägande och auktoritet

## Verksamhetsansvar

Domänen skiljer tre relationer som beskriver olika slags kontroll: personlig
provinstilldelning, en titels säte och en persons relation till ett jarldöme.
Relationerna får inte härledas automatiskt från varandra.

## Centrala begrepp

- **Personlig provinsägare**: nod på nivå 0–2 som fungerar som ankare för ett
  jarldömes personliga provinsväg.
- **Personlig provinsväg**: härledd lista av administrativa förfäder fram till
  valt ägarankare.
- **Titel**: nod på nivå 0–2 som kan ha ett explicit säte.
- **Säte**: jarldöme på nivå 3 inom titelns administrativa delträd.
- **Jarldömesägare**: person i det globala personregistret som explicit
  relaterats till ett jarldöme.
- **Administrativ intäkt** respektive **personlig intäkt**: skilda vyer av
  skatteflödet.

## Bekräftade regler

1. Ett jarldöme kan tilldelas högst ett personligt ägarankare på nivå 0, 1
   eller 2, eller sakna sådan tilldelning.
2. Ankaret måste finnas på angiven nivå och får varken vara jarldömet självt
   eller en av dess efterkommande.
3. En explicit ägare på en undernod bryter nedärvningen från en överordnad
   personlig ägare i provinsvyn.
4. Skatteandelarna normaliseras till intervallet 0–1 och därefter så att
   lokal andel och vidarebefordrad andel tillsammans utgör hela inkomsten.
5. Ett titel–säte måste gå från nivå 0–2 till ett unikt jarldöme på nivå 3 i
   titelns delträd. Samma jarldöme får inte vara säte för flera titlar.
6. En jarldömesägare måste finnas i det globala personregistret.
7. Relationsvalidering får inte mutera världsdata. En skrivoperation får
   mutera först när hela relationen är giltig.
8. Ändrad personlig provinsägare skapar en inspektionssnapshot och publicerar
   en ägarändringshändelse när en händelsebuss finns.

## Domängränser

- Administrativ hierarki och nodnivåer kommer från världsstrukturen.
- Personidentitet kommer från personer och hushåll.
- Domänen definierar skattevägen men inte produktionen av den beskattningsbara
  inkomsten.

## Kvalitetskontroll

- **Tvetydighet:** ordet "ägare" betecknar både provinsankare och
  jarldöme–person; krav och UI behöver konsekvent kvalificerade namn.
- **Otydlighet:** sink-nivåerna i Modell B finns i kod men deras fullständiga
  verksamhetsbetydelse och bokföring är inte dokumenterade.
- **Öppen produktfråga:** titel–säte och jarldömesägare är läsbara i ordinarie
  UI, men framtida redigeringsansvar är inte beslutat.

## Historik

- Ändringar kommer att sparas i `ownership-and-authority.Changelog.md`.
