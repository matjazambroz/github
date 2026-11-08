# eSlog XML (ustvari agent)

Izvajalci naložijo samo PDF, XTRF XML ne ustvari. Zato XML za vsak račun ustvari agent (Graditelj)
iz podatkov, ki jih je razpoznal Strateg, in ga priloži osnutku skupaj s PDF.

## Stanje (8. 11. 2026)
V mapi so `eslog.xsd`, `vzorec.xml` in `xmldsig-core-schema.xsd` (glej `VERZIJA.txt` za izvor in kontrolne vsote).
`./validate.sh vzorec.xml` vrne 0, kar pomeni, da validacija deluje. Pri novem XML-ju torej ne velja več `[XML NEPREVERJEN]`,
če `validate.sh` vrne 0. Shema preverja strukturo, ne vsebinske pravilnosti za Slovenijo (npr. pravilne kode, ID za DDV):
te preveri QA z vzorcem in servis.

## Vir (uradni) in posodabljanje
Uradni paket (XSD, dokumentacija) objavlja ePOS: https://epos.si/eslog. Zadnji znani paket je zapisan v `VERZIJA.txt`
(trenutno `e-SLOG-2.0-08-2020-SL.zip`, preverjeno 8. 11. 2026). Strežnik ima zaščito pred boti, zato paket prenesete
**ročno v brskalniku** in ga razširite v to mapo (XSD kot `eslog.xsd`, vzorec računa kot `vzorec.xml`).
Skripta `./preveri-verzijo.sh` prebere javno stran in sporoči, ali je izšel drug paket kot zapisan (izhod 0 = enako,
1 = drugače, 2 = ni mogoče preveriti). Graditelj jo zaženi pred ustvarjanjem XML-ja in ob izhodu 1 to napiše v osnutku/poročilu.
Pozor: ePOS paket je shema in dokumentacija; ali je v njem tudi vzorčni XML računa, ni preverjeno. Če ga ni, vzorec dobite od servisa.

## Potrebno od računovodskega servisa (če v paketu ePOS ni vzorca ali če sprejemajo drugačno različico)
1. `eslog.xsd` (shema, ki jo sprejme aplikacija e-računi) -> shrani v to mapo.
2. `vzorec.xml`: en pravi sprejet XML prejetega računa -> shrani v to mapo.
Besedilo vprašanja: `vprasanje-servisu.md`.

## Postopek ustvarjanja (Graditelj): skripta `ustvari_xml.py`
XML ustvari deterministična skripta (samo standardna knjižnica Pythona), ne prosto pisanje.
1. Enkrat: `cp kupec.primer.json kupec.json` in vpiši podatke Amidas (naziv, naslov, ID za DDV). `kupec.json` ni v gitu.
2. Strategov izhod za račun pretvori v JSON po vzorcu `primer-racun.json` (dobavitelj, datumi, postavke, neto/DDV/bruto s PDF-ja v `skupaj`).
3. `./ustvari_xml.py racun.json Računi/LLLL-MM/<št. računa>.xml`
4. Izhodna koda: 0 = XML veljaven proti XSD; 1 = napaka vhoda (npr. `skupaj` se ne ujema z izračunom iz postavk: nič se ne zapiše,
   račun dobi ZASTAVICO); 2 = XML zapisan a nepreverjen (manjka `xmllint`/XSD); 3 = validacija pade; 4 = `kupec.json` še ni izpolnjen.
5. Pripni XML in PDF osnutku. Pri kodah 2 in 3 osnutek dobi zadevo `[XML NEPREVERJEN] Račun ...` in zastavico.
Skripta znesek računa izračuna iz postavk in ga primerja s PDF (toleranca 0,02), zato napaka pri branju PDF-ja ne pride v XML.
Testi: `python3 -m unittest -v test_ustvari_xml` (v tej mapi, 12 testov).
**Kode, ki jih servis mora potrditi:** kategorija DDV (privzeto `S` pri stopnji > 0, `E` pri 0 %; reverse charge `AE` ipd. se nastavi
ročno v postavki `kategorija`), kvalifikatorji zneskov (79, 389, 388, 9, 176) in `FTX AAI`. Povzeti so po `vzorec.xml`; ujemanje
z zahtevami e-računov ni preverjeno, preverjena je samo veljavnost proti shemi.

## Pravila skladnosti XML <-> PDF
Dobavitelj, ID za DDV, št. računa, datumi, valuta, neto, DDV, bruto, IBAN in sklic v XML se morajo
natančno ujemati s PDF in z evidenco. Vsako neujemanje = napaka (QA: padec).
