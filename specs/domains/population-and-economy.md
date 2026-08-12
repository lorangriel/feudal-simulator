# Domän: befolkning och ekonomi

## Verksamhetsansvar

Domänen beskriver lokala människor, arbete, lager och nuvarande enkla
intäkter samt hur värden får summeras genom världens hierarki. Den är ännu
inte en fullständig produktions-, konsumtions- eller handelsmodell.

## Centrala begrepp

- **Befolkningsgrupp**: fria bönder, ofria bönder, trälar eller borgare.
- **Lokalt bidrag**: värde som har sitt ursprung på en nod och därför får
  räknas exakt en gång i en rekursiv sammanställning.
- **Dagsverken**: arbetsplikt för ofria bönder med en vald nivå.
- **Tillgängligt arbete**: arbetsdagar från trälar, ofria bönder och anlitade
  daglönare enligt respektive faktor.
- **Arbetsbehov**: lokalt registrerat behov; fiskevatten använder antal båtar.
- **Lager**: fysisk resursnod för basvaror, lyxvaror, silver och råmaterial.
- **Licensintäkt**: nuvarande schablonintäkt från hantverkare.

## Bekräftade regler

1. Lokal befolkning är summan av uttryckliga befolkningsgrupper när sådana
   fält finns. Vildmark och jaktmark har ingen befolkning.
2. Ett redan aggregerat värde på en föräldranod får inte återräknas som lokalt
   bidrag. Lövnoder kan använda ett äldre `population`-fält som reserv.
3. Negativa eller ogiltiga lokala tal bidrar med noll vid sammanställning.
4. Endast `Lager`-noder bidrar med fysisk lagring till rekursiva rapporter.
5. Tillgängligt arbete beräknas från trälar, ofria bönder och anlitade
   daglönare. Dagsverkesnivån styr de ofria böndernas faktor.
6. Arbetsbehov på administrativa nivåer 0–3 bidrar inte lokalt. Hav och flod
   använder fiskebåtar multiplicerat med träls arbetsdagsfaktor.
7. Hantverkares licensintäkt bygger på en fast avgift per yrkestyp och lagrat
   antal.
8. Personlig skattefördelning konsumerar en beräknad jarldömesintäkt men hålls
   begreppsligt skild från administrativ resursredovisning.

## Domängränser

- Världsstrukturen anger var lokala bidrag finns och hur de traverseras.
- Ägande och auktoritet avgör vem som behåller eller tar emot vidarebefordrad
  skatt.
- Väder kan senare påverka produktion, men någon sådan komplett koppling är
  inte ett bekräftat nulägesflöde.

## Kvalitetskontroll

- **Glapp:** produktion, konsumtion, priser, handel och faktiskt skatteunderlag
  saknar sammanhängande regler och acceptanskriterier.
- **Tvetydighet:** `population` kan vara lokalt arvfält eller aggregerat värde;
  den lokala bidragspolicyn mildrar men eliminerar inte datatvetydigheten.
- **Otydlighet:** relationen mellan arbetsbehov, tillgängligt arbete,
  umbärande och resursutfall är inte specificerad som ett årsflöde.

## Historik

- Ändringar kommer att sparas i `population-and-economy.Changelog.md`.
