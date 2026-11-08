---
name: preizkus-racunov
description: Preizkusi verigo prejetih računov na 4 izmišljenih PDF računih (Strateg -> preslikava -> skripta za XML) in primerjaj rezultat s pričakovanim. Ne dotika se Gmaila, XTRF, Sheets ali Drive. Sproži z /preizkus-racunov.
---
# /preizkus-racunov

Preizkus brez pravih podatkov. **Ne uporabljaj** Gmaila, XTRF, Sheets ali Drive; ničesar ne pošiljaj, ne ustvarjaj osnutkov.

## 1. Poišči mapo s preizkusnimi podatki
Prva obstoječa od: `accounting-agent/testni-podatki/` (v trenutnem repozitoriju), `~/.claude/testni-podatki/`. Mora vsebovati
`racun-1..4-*.pdf`, `pricakovano.json`, `preveri_strateg.py` in `kupec-testni.json`; poleg nje mora biti `eslog/` z `ustvari_xml.py`.
Če mape ni, povej, kaj manjka (`install.sh` jo kopira), in ustavi.

## 2. Strateg
Zaženi agenta `racuni-strateg` (Agent tool) z navodilom: preberi samo 4 lokalne PDF-je iz te mape, vrni **samo** JSON seznam po
`eslog/preslikava.md` (en objekt na račun, `prejeto` = današnji datum). Ne dodajaj opomb zunaj JSON-a. Ne pošiljaj mu datoteke
`pricakovano.json` ali `strateg-idealen.json`: preizkus mora preveriti, kaj Strateg ugotovi sam.

## 3. Shrani izhod
Iz Strategovega odgovora izvleci JSON in ga shrani v `strateg-izhod.json` v mapi preizkusa. Preveri, da je veljaven JSON.
Če ni veljaven: ustavi, pokaži težavo in **ne popravljaj ročno**. Izhod Stratega spreminjaš samo, če ga je treba prepisati iz
koda v datoteko, vsebine nikoli ne prilagajaj tako, da bi preizkus prestal.

## 4. Preverjalnik
`python3 preveri_strateg.py strateg-izhod.json` v mapi preizkusa (potreben `xmllint`; če ga ni, to povej in ustavi).

## 5. Poročilo uporabniku
- Skupni rezultat (VSE V REDU ali N napak) in tabela po računih.
- Za vsako NAPAKA: kaj je bilo pričakovano, kaj je Strateg vrnil, in verjeten vzrok (Strategov prompt, preslikava, pričakovanje ali skripta).
  Če je očitno pričakovanje preozko (npr. zastavica drugače zapisana, a pravilna), tako povej, vendar **pričakovanja ne spreminjaj brez
  potrditve uporabnika**.
- Kaj preizkus ne pokrije: Gmail, XTRF, priponke, Sheets, osnutki, pravi (skenirani) PDF-ji; veljavnost XML je samo proti shemi.
- Predlagaj naslednji korak (npr. popravek Stratega) in počakaj na potrditev.
