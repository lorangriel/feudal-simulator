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
