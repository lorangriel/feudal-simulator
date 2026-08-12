# Dahlsdal-arbetsboken

## Status och användning

- Källfil: [`Dahlsdal.xlsx`](Dahlsdal.xlsx).
- Materialtyp: bevarat evidens och referensmaterial.
- Arbetsboken är **inte** en styrande specifikation. Uppgifter i den ska inte
  föras över till levande specifikationer utan separat granskning och beslut.
- Vid frågor får arbetsboken och denna innehållsbeskrivning användas som källa,
  men påståenden bör anges som uppgifter ur Dahlsdal-underlaget snarare än som
  fastställda projektregler.

## Filidentitet

- Filstorlek: 1 252 992 byte.
- SHA-256:
  `2d06791effff61833cd766e77b08c5a14bc7b3abe5d301551df03fc877659482`.
- Format: Excel Open XML (`.xlsx`).
- Omfattning: 24 kalkylblad med både inmatade värden, anteckningar och formler.

Kontrollsumman identifierar den bevarade version som beskrivs här. Formlerna
har inventerats men inte räknats om eller validerats mot spelets regler.

## Övergripande innehåll

Arbetsboken är ett omfattande beräknings- och planeringsunderlag för
förläningen Dahlsdal. Den kombinerar en sammanställning över förläningen med
historiska årsblad, prognoser, ekonomiska kalkyler och specialblad för bland
annat borg, hjordar, hushåll, förläningar, grannar och biodling. Års- och
prognosbladen behandlar återkommande områden som befolkning, byar och gods,
dagsverken, markkvalitet, väder, inkomster och utgifter i BAS/LYX, soldater,
hästar, odling, djurhållning, jakt, fiske, handel, hantverk och järnproduktion.

Materialet innehåller också arbetskopior och testblad. Dessa visar att flera
alternativa beräkningar har provats och ska därför inte automatiskt betraktas
som slutliga eller inbördes förenliga.

## Idéer och visioner i arbetsboken

Statusmarkeringarna nedan beskriver endast om en igenkännbar motsvarighet
finns i kodbasen i dag:

- **[PRESENT]**: idéns grundform finns i kodbasen. Markeringen innebär inte att
  arbetsbokens regler, värden eller formler har implementerats.
- **[NOT IMPLEMENTED]**: någon motsvarande funktion har inte identifierats i
  kodbasen. Delvis närliggande datatyper eller UI-fält räcker inte för denna
  markering.

Inventeringen samlar idéerna tematiskt och avduplicerar upprepningar mellan
års-, prognos-, test- och kopieblad. Den är ett register över historiskt
material, inte en kravlista eller en bedömning av vad vi bör bygga.

### Värld, mark och förvaltning

- **[PRESENT]** Hierarkiska förläningar med gods, bosättningar, vildmark,
  jaktmark, mark, vatten och underliggande områden.
- **[PRESENT]** Grannrelationer och olika slags gränser eller förbindelser,
  bland annat vägar, vildmark, berg och vattendrag.
- **[PRESENT]** Indelning av mark i skog, röjd mark, odling, träda, bete och
  jaktmark samt kvalitetsvärden för odling, jakt och fiske.
- **[NOT IMPLEMENTED]** Arbetsbokens arealomvandlingar och investeringar:
  röjning av vildmark, avverkning, nyodling, diken, bevattningsdammar,
  fiskdammar, vingårdar, olivlundar och deras underhåll.
- **[NOT IMPLEMENTED]** En skalbestämd rutkarta om 256 × 256 rutor med
  tunnland per ruta.
- **[NOT IMPLEMENTED]** Förvaltares kontrollslag, kapacitetsgränser,
  lärlingar, färdigheter och svårighetsökning när en näring eller areal blir
  större.

### Befolkning, hushåll och samhälle

- **[PRESENT]** Befolkningsgrupperna fria och ofria bönder, trälar,
  daglönare och borgare samt personer knutna till världens entiteter.
- **[PRESENT]** Personliga provins- och ägarrelationer samt listor över
  hantverkare, soldater och andra roller.
- **[PRESENT]** Adliga levnadsnivåer, bostadskrav, familje-/hushållsmedlemmar
  och behov av namngivna hushållsroller.
- **[NOT IMPLEMENTED]** Full hushållsekonomi med åldersgrupper, utspisning,
  beskattningsunderlag, engångskostnad för möbler, BAS-/LYX-underhåll och
  besparingar.
- **[NOT IMPLEMENTED]** Befolkningstillväxt, inflyttning, nybyggare och
  hantverkarflytt som resultat av umbäranden eller övertag.
- **[NOT IMPLEMENTED]** Böndernas lojalitet, tro, heder och uppror samt hur
  väder, kyrka, skatt, avrad och dagsverken påverkar dem.
- **[NOT IMPLEMENTED]** Rykte, tjänster/favours, allianser, fester,
  storslagna jakter och levnadsstandardens skydd mot sjukdom.

### Tid, väder och historik

- **[PRESENT]** Årsvis framskrivning med planeringsläge och låsta snapshots,
  vilket motsvarar arbetsbokens idé om separata årsunderlag på en övergripande
  nivå.
- **[PRESENT]** Vår-, sommar-, höst- och vinterväder med effekter på
  produktion och umbäranden.
- **[NOT IMPLEMENTED]** En sammanhållen simulering som räknar om samtliga
  ekonomiska och demografiska årsresultat från arbetsboken.
- **[NOT IMPLEMENTED]** Arbetsbokens särskilda katastrofer och motgångar,
  exempelvis farsot, pest, kättare, rövarband, monsterräder, nomader och
  uppviglare, med efterverkningar mellan år.

### Arbete, produktion och lager

- **[PRESENT]** Dagsverksnivåer, tillgängligt och behövligt arbete samt
  umbärande som lagrade egenskaper och grundläggande beräkningar.
- **[PRESENT]** Lager för silver, BAS, LYX, timmer, kol, järnmalm, järn,
  djurfoder och skinn.
- **[PRESENT]** Grundtyper för odling, djurhållning, jakt, fiske,
  hantverkare, byggnader, soldater och båtar.
- **[NOT IMPLEMENTED]** Arbetsbokens sammanlänkade produktionskedjor och
  balansformler för skörd, träda, foder, jakt, fiske, timmer, träkol,
  järnmalm, järn, stål, vapen, skinn och garvning.
- **[NOT IMPLEMENTED]** Kvalitets- och kontrollslag som ger förlust,
  normalutfall, bonusproduktion, LYX-andel eller framtida
  kvalitetsförändringar.
- **[NOT IMPLEMENTED]** Licensavgifter som en körd ekonomisk process; yrken
  och avgiftsvärden finns, men arbetsbokens intäktsflöde simuleras inte.

### Djur, jakt, fiske och specialnäringar

- **[PRESENT]** Registrering av djur och hästtyper, hjordmarkering,
  betesareal, jägare, jaktkvalitet, jaktlagstiftning, fiskekvalitet och antal
  fiskebåtar.
- **[NOT IMPLEMENTED]** Hjordstorlekar, vinterflockar, fortplantning,
  dubbleringstid, slakt, mjölk, ull, skinn, foderåtgång och väderberoende
  avkastning för kor, får/getter och grisar.
- **[NOT IMPLEMENTED]** Hästavel, stuteristorlekar, fölålder, rid- och
  stridsträning samt skötsel-, foder- och betesbehov per hästtyp.
- **[NOT IMPLEMENTED]** Jaktlagens bemanning, arealkrav, kostnad och avkastning
  samt skogsbetets negativa effekt på jakt.
- **[NOT IMPLEMENTED]** Fiskdammssystem med anläggning, foder, förvaltning,
  kvalitetsutveckling, sjukdom och årsutfall.
- **[NOT IMPLEMENTED]** Biodling i tre storlekar med investerings- och
  skötselbehov, pollineringsbonus, BAS/LYX-produktion, avläggare och
  katastrofutfall.

### Handel, skatt och transporter

- **[NOT IMPLEMENTED]** Lokala och provinsiella marknader, mat- och
  råvarupriser, import/export samt handelsvolym i BAS, LYX och silver.
- **[NOT IMPLEMENTED]** Handelsvägar via liten/stor väg, flod, kust och hav,
  med skilda multiplikatorer, tullar och kontrollslag.
- **[NOT IMPLEMENTED]** Handelsmäns färdigheter, vakter, handelsavtal,
  handelsstäder, aktiv handel och förlorad eller kvarvarande handelsvolym.
- **[NOT IMPLEMENTED]** Båtbygge och fartygsmodeller med mått, djupgående,
  besättning, lastdryghet, hytter, stall, byggtid, arbete och material.
- **[NOT IMPLEMENTED]** Skatt, avrad, kungaskatt, tull, skulder och lån som
  sammanhängande ekonomiska flöden. Kodbasen har fördelningsandelar och
  lagringsfält men inte arbetsbokens modell.

### Byggnader, borg och militär

- **[PRESENT]** Registrering av bland annat trähus, stenhus, borgkärna,
  kvarnar, bageri, smedja och garveri.
- **[PRESENT]** Registrering av flera soldattyper, officerare, riddare och
  sjömän.
- **[NOT IMPLEMENTED]** Byggprojekt med material, dagsverken, silverkostnad,
  byggtid och underhåll för hus, vägar, kvarnar, verkstäder, torn, murar,
  vallgrav och borgkärna.
- **[NOT IMPLEMENTED]** Borgens rumsliga plan, våningar, rum, bemanning och
  härledning av sten- eller byggnadsvolym.
- **[NOT IMPLEMENTED]** Militär rekrytering, lön, utrustning, färdigheter,
  tjänstgöringstid och administrativa bemanningskrav för gods, trälar och
  daglönare.

### Avgränsning mot våra levande specifikationer

Denna katalog och arbetsboken är endast historisk evidens. **Varken
[PRESENT]- eller [NOT IMPLEMENTED]-poster får användas för att skapa, ändra,
prioritera eller tolka våra nuvarande specifikationer.** [NOT IMPLEMENTED]
uttrycker inte ett planerat behov, och [PRESENT] bekräftar endast en grov
funktionsmotsvarighet. Arbetsbokens världs- och entitetsdata, regler,
balansformler, simuleringar och årsutfall är inaktuella inför den planerade
omstarten och har inte validerats. Eventuella framtida krav måste tas fram och
beslutas oberoende av detta underlag.

## Kalkylblad

| Blad | Omfång | Icke-tomma celler | Formler | Innehåll i korthet |
| --- | ---: | ---: | ---: | --- |
| `Dahlsdal` | `A1:AB77` | 197 | 54 | Sammanställning över förläningen, marknader, matpriser samt byggnader och byggnation per år. |
| `prognos år 15` | `A1:BK1004` | 1 787 | 612 | Långsiktig prognos för befolkning, dagsverken, ekonomi, gods, militär, djur, järn och produktion. |
| `Borg` | `A1:FA1004` | 275 | 1 | Rutnätsliknande skiss över borgens våningar och rum, med markeringar för bland annat trappor, salar, sovrum, kök, soldater och vakter. |
| `Hjordar` | `A1:AY1004` | 523 | 186 | Kalkyler för kor, får/getter, grisar och hästar: bete, avkastning, vinterflock, foder, dagsverken och kostnader. |
| `Hushålltjänstefolk` | `A1:AE242` | 445 | 88 | Hushållets levnadsstandard, familj, bostadskrav, tjänsteroller, utspisning, beskattning och BAS/LYX-kostnader. |
| `Förläningar` | `A1:Z282` | 848 | 117 | Anteckningar och kalkyler om markröjning, skog, odling, dagsverken, produktion, umbäranden och förvaltningsbehov. |
| `Grannar, alla` | `A1:Z281` | 490 | 0 | Förteckningar över grannområden, personer samt antal gods och byar. |
| `Biodling` | `A1:AH1000` | 284 | 100 | Specialkalkyl för biodling tillsammans med markarbete, investering, produktion och relaterade kostnader. |
| `År -5` | `A1:AA1002` | 348 | 87 | Tidigt historiskt årsunderlag. |
| `År -4` | `A1:AA1002` | 368 | 88 | Historiskt årsunderlag. |
| `År-3` | `A1:AA1002` | 380 | 88 | Historiskt årsunderlag. |
| `År-2` | `A1:AA1002` | 385 | 88 | Historiskt årsunderlag. |
| `År-1` | `A1:AA1002` | 399 | 88 | Historiskt årsunderlag. |
| `År 1` | `A1:AD1002` | 443 | 91 | Årsunderlag med utökade beräkningar. |
| `År 2` | `A1:BJ1004` | 1 151 | 366 | Detaljerat årsunderlag för ekonomi, befolkning, arbete och produktion. |
| `År 3` | `A1:BK1004` | 1 779 | 612 | Detaljerat årsunderlag och bas för senare test- och prognosvarianter. |
| `Test` | `A1:BK1004` | 1 779 | 612 | Testkopia av den detaljerade årsmodellen. |
| `Test mat` | `A1:BK1004` | 1 774 | 630 | Testvariant med fokus på matrelaterade beräkningar. |
| `Blir År 4` | `A1:BK1004` | 2 064 | 693 | Prognos/arbetsversion inför år 4. |
| `Kopia av Blir År 4 2` | `A1:BK1004` | 2 066 | 693 | Kopia och alternativ arbetsversion inför år 4. |
| `test av storlek på giftasgods` | `A1:BK1004` | 2 027 | 693 | Testvariant för storleken på ett giftas-/giftermålsgods. |
| `Kopia av Blir År 4 1` | `A1:BK1004` | 2 002 | 678 | Kopia och alternativ arbetsversion inför år 4. |
| `Kopia av Blir År 4` | `A1:BK1004` | 2 008 | 677 | Kopia och alternativ arbetsversion inför år 4. |
| `Dahlsdah 3.0 år 4` | `A1:BJ1004` | 2 041 | 689 | Senare år 4-variant med omdisponerade ekonomi-, försörjnings- och produktionsberäkningar. |

## Viktiga tolkningsbegränsningar

- Bladnamn som `Test`, `Kopia` och `Blir` markerar arbetsmaterial eller
  alternativ, inte nödvändigtvis beslutade värden.
- Stavning och namn varierar i arbetsboken, exempelvis `Dahlsdal`, `Dahsdal`
  och `Dahlsdah`. Beskrivningen normaliserar inte källdata.
- Stora använda områden beror delvis på formatering och tomma modellområden;
  tabellen redovisar därför även antalet faktiskt icke-tomma celler.
- Formler kan bero på andra celler i samma blad. Innehållet ska granskas i sitt
  sammanhang innan ett enskilt värde citeras.

## Historik

- Ändringshistorik finns i `dahlsdal-workbook.Changelog.md`.
