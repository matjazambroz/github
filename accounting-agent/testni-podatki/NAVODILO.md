# Preizkus verige na izmišljenih računih

Štirje izmišljeni PDF računi (vsi nosijo opozorilo "IZMIŠLJEN RAČUN, SAMO ZA PREIZKUS"). Preizkus ne potrebuje Gmaila, XTRF ali Sheets:
preveri **Stratega** (branje PDF in sestava JSON), **preslikavo** in **skripto za XML**.

| Datoteka | Past | Pričakovan rezultat |
|---|---|---|
| `racun-1-domaci-ddv22.pdf` | domači s.p., 22 % DDV, dve postavki | brez zastavic, konto 4100, neto 150,00, DDV 33,00, bruto 183,00, XML veljaven |
| `racun-2-sp-brez-ddv.pdf` | s.p. brez DDV (oprostitev na računu) | brez zastavic, stopnja 0, konto 4100, bruto 240,00, XML veljaven (kategorija E) |
| `racun-3-tuj-izvajalec.pdf` | nemški izvajalec, reverse charge | ZASTAVICA (tuj izvajalec, reverse charge za servis), konto 4102, osnutka za servis ni |
| `racun-4-racunska-napaka.pdf` | skupni znesek 71,00 namesto 61,00 | zastavica, `preverjanja.matematika` = napaka, skripta zavrne XML (koda 1) |

## Koraki
1. **Strateg bere PDF-je** (v Claude Code, v korenu repozitorija):
   > Uporabi agenta racuni-strateg na PDF-jih `accounting-agent/testni-podatki/racun-*.pdf`. Bere naj samo te lokalne datoteke
   > (ne Gmaila, XTRF-ja ali Sheets). Izhod naj bo JSON seznam po `eslog/preslikava.md`. Izhod shrani v
   > `accounting-agent/testni-podatki/strateg-izhod.json`.
   Opomba: Strateg nima orodja za pisanje, zato datoteko shrani glavni agent iz Strategovega odgovora.
2. **Preverjalnik** (potreben `xmllint`):
   ```bash
   cd accounting-agent/testni-podatki && python3 preveri_strateg.py strateg-izhod.json
   ```
   Za vsak račun izpiše OK/NAPAKA za podatke, konto, zastavice, matematiko in izhodno kodo `ustvari_xml.py` (s testnim kupcem,
   zato `kupec.json` Amidas ni potreben). Izhod 0 = vse v redu.
3. **Poglej napake.** Pričakovane težave: Strateg lahko drugače zapiše zastavico (preverjalnik išče besede reverse/tuj/obrnjen
   in matemat/znesek/bruto), ali pa drugače izbere konto. Preglej vsako NAPAKA ročno, preden spremeniš agenta ali pričakovanje.
4. **Kontrola samega preizkusa** (brez Stratega): `python3 preveri_strateg.py strateg-idealen.json` mora vrniti VSE V REDU.
   Ponovna izdelava računov in pričakovanj: `python3 ustvari_testne_racune.py`.

## Česa ta preizkus NE pokrije
- Gmail, XTRF in priponke (ali agent dobi PDF iz e-pošte), vpis v Sheets, osnutki, oznake.
- Branje pravih računov: izmišljeni PDF-ji so čisti (besedilni sloj, lepa postavitev); pravi so lahko skenirani ali drugače razporejeni.
- Ali aplikacija e-računi sprejme XML (preverjena je samo veljavnost proti shemi).

## Če boste kasneje preizkusili še Graditelja (Sheets, Gmail, Drive)
Uporabite ločeno testno preglednico in testno Drive mapo, ne prave evidence. Osnutki gredo na pravi naslov servisa:
pred preizkusom zamenjajte prejemnika v osnutku ali ga izbrišite, preden kdo pošlje. Račune iz te mape po preizkusu odstranite iz evidence.
