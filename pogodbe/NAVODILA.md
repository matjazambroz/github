# Pregled pogodb

Samostojna aplikacija za Windows 10/11. Ne potrebuje namestitve, Pythona ali interneta.

## Zagon
Razpakirajte ZIP in zaženite `PregledPogodb.exe`.

## Uporaba
1. **Uvozi datoteke / Uvozi mapo** (ali povlecite datoteke v okno). Podprto: PDF (besedilni in skenirani), slike (PNG, JPG, TIFF), Word (.docx).
2. Skenirane strani se samodejno preberejo z OCR (slovenščina + angleščina). Uvoz skeniranih pogodb traja nekaj sekund na stran.
3. Aplikacija izlušči: naslov, številko, vrsto, stranki (z matično/davčno številko), datum sklenitve, veljavnost (od–do, trajanje,
   nedoločen čas, samodejno podaljšanje, odpovedni rok), vrednost (z valuto, DDV, obdobjem), plačilni rok, predmet in **strukturo (člene, priloge)**.
4. Pogodbe so obarvane po statusu: zeleno veljavna, rumeno poteče v 90 dneh, rdeče pretečena, modro nedoločen čas.
5. Zavihek **Podatki** pokaže, od kod je bil podatek prebran (z oceno zanesljivosti) – napačne podatke popravite in shranite.
   Zavihek **Struktura** prikaže člene, **Besedilo** celotno vsebino z iskanjem.
6. Iskalno polje išče po vsebini vseh pogodb. **Izvozi v Excel** shrani pregled.

## Podatki
Zbirka je v `%LOCALAPPDATA%\PregledPogodb\pogodbe.db`. Izvirne datoteke se ne kopirajo – aplikacija si zapomni pot do njih.
Vse poteka lokalno; pogodbe ne zapustijo računalnika.

## Natančnost
Izluščanje temelji na pravilih, zato je pri nenavadnih oblikah ali slabih skenih lahko napačno. Ocena "nizka" pomeni, da podatek preverite.
