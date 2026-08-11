# Kvarstående specifikationsfrågor

## P0 – blockerar tidsplanering

1. Ska årsmodellen i `src/time/time_engine.py` vara styrande, eller ska den
   säsongsbaserade modellen i `src/time_engine.py` ersätta den?
2. Ska historiska ändringar behålla låsta snapshots, regenerera en enda
   framtid eller skapa förgrenade tidslinjer?

## P1 – blockerar domänavgränsning

1. Vilket minsta ekonomi-, händelse- och relationsflöde definierar den första
   kompletta simuleringen, med mätbara acceptanskriterier?
2. Ska titel–säte och jarldöme–ägare förbli skrivskyddade i användargränssnittet
   eller få ett framtida redigeringsflöde utanför admin-läget?
3. Hur ska termen "ägare" namnges i krav och UI så att personlig
   provinstilldelning inte sammanblandas med jarldömets personrelation?

## Historik

- Ändringar kommer att sparas i `outstanding-questions.Changelog.md`.
