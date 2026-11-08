# Evidenca prejetih računov (Google Sheets)

Datoteka `evidenca-prejeti-racuni.csv` vsebuje samo glavo. Uvoz: Sheets -> Datoteka -> Uvozi -> Naloži ->
**Ustvari novo preglednico**, ločilo vejica. Poimenuj preglednico **Prejeti računi**, prvi list **Racuni**,
njen ID vpiši v `memory/reference_viri.md`. Agent dodaja samo nove vrstice na dno (append), obstoječih ne spreminja,
razen stolpcev status, zastavice, qa_ocena in opomba v vrstici, ki jo sam ustvaril.

## Stolpci (vrstni red je dogovor: Graditelj piše po njem)
| # | Stolpec | Pomen | Primer oblike |
|---|---|---|---|
| A | datum_prejema | datum, ko je račun prispel | 2026-11-08 |
| B | dobavitelj | polno ime | Jana Novak s.p. |
| C | id_za_ddv | ID za DDV ali prazno (ni zavezanec) | SI12345678 |
| D | st_racuna | številka računa natanko kot na PDF | 2026-014 |
| E | datum_racuna | | 2026-11-05 |
| F | zapadlost | | 2026-12-05 |
| G | valuta | ISO koda | EUR |
| H | neto | številka, pika kot decimalka | 450.00 |
| I | stopnja_ddv | 22, 9.5, 5, 0 ali prazno | 22 |
| J | ddv | | 99.00 |
| K | bruto | mora biti H + J | 549.00 |
| L | iban | brez presledkov | SI56... |
| M | sklic | | SI00 2026-014 |
| N | konto | iz `kontni-nacrt.md`, predlog | 4100 |
| O | xtrf_projekt | ID projekta/joba iz XTRF | 86652 |
| P | status | glej spodaj | PRIPRAVLJENO |
| Q | zastavice | vrednosti ločene s podpičjem | TUJ IZVAJALEC; IBAN SPREMENJEN |
| R | qa_ocena | 0 do 100 | 97 |
| S | povezava_pdf | Drive povezava | |
| T | povezava_xml | Drive povezava | |
| U | povezava_osnutek | povezava do Gmail osnutka | |
| V | paket | številka osnutka/paketa | 2026-11 / 03 |
| W | opomba | prosto besedilo (tudi vaša) | |

## Vrednosti stolpca status
`NOVO` -> `PREVERJENO` -> `PRIPRAVLJENO` -> `POSLANO SERVISU`, ob težavi `ZASTAVICA`.
**POSLANO SERVISU nastavite samo vi**, ko osnutek pošljete. Brez tega rutina 12. in 16. v mesecu ne ve, kaj je že poslano.

## Priporočene nastavitve v Sheets (ročno, enkrat)
1. Podatki -> Preverjanje podatkov na P2:P: spustni seznam z zgornjimi statusi.
2. Zamrzni vrstico 1 in stolpec B.
3. Pogojno oblikovanje na celotni vrstici A2:W:
   - rdeče, če `=$P2="ZASTAVICA"`
   - rumeno, če `=AND($P2="PRIPRAVLJENO";$Q2<>"")`
   - rdeče besedilo v K, če `=ABS($K2-($H2+$J2))>0.02`
4. Neobvezen pomožni stolpec X "dvojnik": `=IF(COUNTIFS($B:$B;$B2;$D:$D;$D2;$K:$K;$K2)>1;"DVOJNIK";"")`
   (v slovenskem jeziku preglednice je ločilo v formulah podpičje).

## Opombe
- Številke naj bodo zapisane s piko in brez ločil tisočic; če jih Sheets v slovenskem jeziku obravnava kot besedilo,
  jih po uvozu pretvori (Oblika -> Številka) ali v Datoteka -> Nastavitve nastavi jezik "Združene države".
- Dodajanje stolpcev na konec je varno, spreminjanje vrstnega reda ali brisanje ni: agent piše po položaju.
