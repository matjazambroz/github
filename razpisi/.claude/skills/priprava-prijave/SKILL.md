---
name: priprava-prijave
description: Orkestrira pripravo prijave na razpis: analiza, osnutek, ponudba, pregled. Uporabi, ko uporabnik želi pripraviti prijavo za razpis v mapi vhod/.
---
Argument: ime mape razpisa v `razpisi/vhod/`.

1. Zaženi samo agenta `analitik-razpisa` in počakaj, da se konča. Preveri, da `izhod/<razpis>/zahteve.md` obstaja in ni prazen. Do takrat NE zaženi nobenega drugega agenta.
2. Šele ko `zahteve.md` obstaja, zaženi `pisec-prijave` in `kalkulant` vzporedno (v enem sporočilu).
3. Zaženi `pregledovalec`; povzemi vrzeli uporabniku.
4. Če so vrzeli, vprašaj uporabnika po manjkajočih podatkih (eno vprašanje naenkrat) in ponovi korak 2 samo za prizadete dele.
