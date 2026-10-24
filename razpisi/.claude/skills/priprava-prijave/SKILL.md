---
name: priprava-prijave
description: Orkestrira pripravo prijave na razpis: analiza, osnutek, ponudba, pregled. Uporabi, ko uporabnik želi pripraviti prijavo za razpis v mapi vhod/.
---
Argument: ime mape razpisa v `razpisi/vhod/`.

1. Zaženi agenta `analitik-razpisa`; počakaj na `zahteve.md`.
2. Vzporedno zaženi `pisec-prijave` in `kalkulant`.
3. Zaženi `pregledovalec`; povzemi vrzeli uporabniku.
4. Če so vrzeli, vprašaj uporabnika po manjkajočih podatkih (eno vprašanje naenkrat) in ponovi korak 2 samo za prizadete dele.
