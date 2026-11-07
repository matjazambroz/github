# eSlog XML (ustvari agent)

Izvajalci naložijo samo PDF, XTRF XML ne ustvari. Zato XML za vsak račun ustvari agent (Graditelj)
iz podatkov, ki jih je razpoznal Strateg, in ga priloži osnutku skupaj s PDF.

## Potrebno od računovodskega servisa (brez tega XML NI preverjen)
1. `eslog.xsd` (shema, ki jo sprejme aplikacija e-računi) -> shrani v to mapo.
2. `vzorec.xml`: en pravi sprejet XML prejetega računa -> shrani v to mapo.
Besedilo vprašanja: `vprasanje-servisu.md`.

## Postopek ustvarjanja (Graditelj)
1. Vzemi strukturirane podatke iz Strategovega JSON (vključno s postavkami računa).
2. Oblikuj XML po `vzorec.xml` (ista struktura, imenski prostori, kode). Ne izmišljaj polj, ki jih vzorec nima.
3. Preveri: `./eslog/validate.sh <datoteka.xml>`. Izhod 0 = veljaven proti XSD.
4. Shrani `Računi/YYYY-MM/<št. računa>.xml` in pripni osnutku.
5. Če `eslog.xsd` ali `vzorec.xml` v mapi ni: XML se vseeno ustvari kot predlog, a osnutek dobi zadevo
   `[XML NEPREVERJEN] Račun ...` in račun status ZASTAVICA ("XML ni preverjen proti XSD").

## Pravila skladnosti XML <-> PDF
Dobavitelj, ID za DDV, št. računa, datumi, valuta, neto, DDV, bruto, IBAN in sklic v XML se morajo
natančno ujemati s PDF in z evidenco. Vsako neujemanje = napaka (QA: padec).
