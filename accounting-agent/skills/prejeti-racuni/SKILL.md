---
name: prejeti-racuni
description: Obdela nove prejete račune (Gmail + XTRF obvestila), jih analizira, vpiše v evidenco in pripravi paket za računovodski servis. Samo priprava, vse potrdi uporabnik. Sproži z /prejeti-racuni.
---
# /prejeti-racuni

## Vhodi (vprašaj samo, česar ni)
- Obdobje (privzeto: od zadnje obdelave oz. zadnjih 7 dni).
- Nastavitve iz memory/reference_viri.md (Sheets ID, Drive mapa, kontakt servisa).

## Potek
1. **Zbiranje**: Gmail iskanje (obvestila XTRF, priponke PDF/XML, oznaka `Računi/Novo`). Podvojenih niti ne obdelaj dvakrat.
2. **Analiza**: agent `racuni-strateg` (Opus) vrne JSON za vsak račun.
3. **Izvedba**: agent `racuni-graditelj` (Sonnet) vpiše v Sheets, označi Gmail, pripravi paket in osnutke.
4. **QA**: agent `racuni-qa`. Če ocena < 95: nazaj Graditelju (max 2 kroga), nato eskalacija.
5. **Predaja uporabniku**: kratek povzetek (št. računov, skupni znesek, zastavice po prioriteti,
   vprašanja za servis, povezave do osnutkov). Čakaj na potrditev.

## Paketi
Obdelaj v enem paketu do 15 računov naenkrat; več jih razdeli v več paketov, vsak s svojim QA krogom.
Če ni novih računov, to povej v eni vrstici in ne ustvarjaj osnutkov.

## Izhod
Tabela povzetka + povezave. Nikoli ne pošlji, ne briši, ne plačaj.

## Po povratni informaciji
Vsak popravek uporabnika zapiši v memory/feedback_*.md in dodaj v MEMORY.md.
