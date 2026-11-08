# Preslikava: Strategov izhod -> skripta `ustvari_xml.py` -> evidenca (Sheets)

Strateg vrne seznam objektov (glej `agents/racuni-strateg.md`, primer: `strateg-primer.json`). Graditelj za vsak objekt:
1. vzame `podatki` in ga **nespremenjenega** shrani kot `racun.json` (to je že vhod skripte; neznani ključi, npr. `xtrf_projekt`, ji ne škodijo),
2. požene `./ustvari_xml.py racun.json <izhod.xml>` in prebere izhodno kodo,
3. vpiše vrstico v evidenco po spodnji tabeli.

## A0) Izven `podatki`: `xml_izvirnik`
Če je izvajalec priložil XML (Gmail priloga ali XTRF), Strateg to zapiše v `xml_izvirnik: {"vir": "gmail:<id>/<ime>"}`, sicer `null`.
`podatki` se vedno razberejo iz PDF-ja. Graditelj nato zažene `pripravi_xml.py ... [--izvirnik <XML>]` (izvirnik, če obstaja).

## A) `podatki` -> vhod skripte (kopija, brez prevajanja)
| Polje v `podatki` | Obvezno | Pravilo |
|---|---|---|
| `st_racuna` | da | natanko kot na PDF |
| `datum_racuna` | da | LLLL-MM-DD |
| `datum_storitve`, `zapadlost` | ne | izpusti, če ju ni na računu |
| `valuta` | da | 3 črke, običajno EUR |
| `sklic` | ne | |
| `dobavitelj.naziv/naslov/mesto/posta` | da | naslov največ 105 znakov, naziv 350 (skripta ga razreže) |
| `dobavitelj.drzava` | ne | privzeto SI |
| `dobavitelj.id_za_ddv` | ne | izpusti za nezavezance (račun brez DDV) |
| `dobavitelj.iban`, `bic` | ne | IBAN se v XML vpiše samo, če je preverjen (`preverjanja.iban` = ok); ob SPREMENJEN ga ne vpiši, račun ZASTAVICA |
| `postavke[].opis` | da | |
| `postavke[].kolicina`, `cena_neto` | da | številki, pika kot decimalka |
| `postavke[].enota` | ne | privzeto `C62` (kos); ure `HUR` |
| `postavke[].stopnja_ddv` | ne | 22, 9.5, 5 ali 0; privzeto 0 |
| `postavke[].kategorija` | ne | privzeto `S` (stopnja > 0) ali `E` (0 %); `AE` (reverse charge) samo po potrditvi servisa |
| `skupaj.neto/ddv/bruto` | priporočeno | zneski s PDF-ja; skripta jih primerja z izračunom, neujemanje = koda 1 |
| `xtrf_projekt`, `opomba` | ne | `opomba` gre v XML (FTX), `xtrf_projekt` samo v evidenco |

**Pravilo "MANJKA":** Strateg v `podatki` nikoli ne piše "MANJKA". Neobvezno polje, ki ga ni, se izpusti. Če manjka obvezno polje,
Strateg račun označi z zastavico in `podatki` ne sestavi popolno. Skripta vsak niz "MANJKA" zavrne (koda 1), da ne pride v XML.

## Pasti pri branju pravih računov (iz računa e-računov, preverjeno 8. 11. 2026)
- **Decimalna vejica in pika za tisočice:** `1,63` -> `"1.63"`, `1.013,50` -> `"1013.50"`.
- **Enota:** na računu je lahko `prev. stran`, `projekt`, `ura`; v `enota` pride koda UN/ECE (`C62` kos/stran/projekt, `HUR` ura), polno ime enote v `opis` ni potrebno.
- **Popust (stolpec R%):** `cena_neto` je cena PO popustu (24,00 s 50 % popustom -> `12.00`), tako da količina × cena da neto postavke.
- **Obdobje storitve** (`01.03.2025-31.03.2025`): `datum_storitve` = zadnji dan obdobja; obdobje samo se zaenkrat ne prenese v XML.
- **Sklic:** zapiši, kot je na računu (npr. `12 2026000000007`).
- **Neto postavke in skupaj morata ustrezati računu** (`skupaj` s PDF-ja); skripta DDV računa na vsoti osnov in ga ob drugačnem zaokroževanju
  dobavitelja (do 0,02, ena stopnja) prevzame s PDF-ja.

## B) Izhodna koda `pripravi_xml.py` -> ukrep (podrobno: `agents/racuni-graditelj.md`)
(0 veljaven; 10 izvirnik ni skladen s PDF; 11 izvirnik neveljaven; 12 nepreverjen; 20 napaka vhoda; 21 generiran neveljaven; 30 kupec ni izpolnjen.)

Starejša tabela za `ustvari_xml.py` (kode 0 do 4) velja samo, kadar se skripta kliče neposredno:
| Koda | Pomen | Status v evidenci | Osnutek za servis |
|---|---|---|---|
| 0 | XML veljaven | PREVERJENO -> PRIPRAVLJENO po QA | da, PDF + XML |
| 1 | napaka vhoda | ZASTAVICA ("XML: " + sporočilo skripte) | ne |
| 2 / 3 | nepreverjen / neveljaven | ZASTAVICA ("XML NEPREVERJEN") | da, zadeva `[XML NEPREVERJEN] ...` |
| 4 | `kupec.json` ni izpolnjen | ne spreminjaj, ustavi vse | ne, obvesti uporabnika |

## C) Strateg -> stolpci evidence (`evidenca-navodilo.md`)
| Stolpec | Vir |
|---|---|
| A datum_prejema | `prejeto` |
| B dobavitelj | `podatki.dobavitelj.naziv` |
| C id_za_ddv | `podatki.dobavitelj.id_za_ddv` (prazno, če ga ni) |
| D st_racuna, E datum_racuna, F zapadlost, G valuta | `podatki.*` |
| H neto, J ddv, K bruto | izračun iz postavk, ki ga izpiše skripta (`neto ... ddv ... bruto ...`); če skripta ni stekla, `podatki.skupaj` |
| I stopnja_ddv | stopnja postavk; pri več stopnjah: seznam, npr. `22; 9.5` |
| L iban, M sklic | `podatki.dobavitelj.iban` (brez presledkov), `podatki.sklic` |
| N konto | `konto_predlog` |
| O xtrf_projekt | `podatki.xtrf_projekt` |
| P status | NOVO, ZASTAVICA ali PRIPRAVLJENO (tabela B); POSLANO SERVISU nastavi samo uporabnik |
| Q zastavice | `zastavice` (ločene s podpičjem) + zastavice iz tabele B |
| R qa_ocena | ocena agenta `racuni-qa` |
| S, T, U | povezave do PDF, XML in osnutka (nastanejo pri Graditelju) |
| V paket, W opomba | številka paketa, `davcno` kot prva vrstica opombe |

Ob nejasnosti med tem dokumentom in agentom velja ta dokument; spremembo ključev je treba narediti hkrati v Strategu, v tem
dokumentu in v testu `test_ustvari_xml.py` (ta preveri, da `strateg-primer.json` deluje v skripti).
