# Predlog kontnega načrta za prejete račune (Amidas, prevajalska agencija)

**STATUS: PREDLOG. Konte in oznake mora potrditi računovodski servis** (ta ima končno besedo
in lahko uporablja svojo razdelitev). Struktura sledi razredom Slovenskih računovodskih standardov
(SRS): razred 4 = stroški, 16 = terjatve za DDV, 22 = obveznosti do dobaviteljev.
Številke podkontov (4. mesto naprej) so interne: servis jih preslika na svoje.

Agent konta samo PREDLAGA. Če račun ne sodi v nobeno vrstico, zapiše "KONTO: ni v načrtu" + ZASTAVICA.

## Stroški (razred 4)
| Konto (predlog) | Naziv | Tipični primeri |
|---|---|---|
| 4100 | Storitve izvajalcev: prevajanje, lektoriranje, DTP | računi prevajalcev, lektorjev (s.p., d.o.o.) iz XTRF |
| 4101 | Storitve izvajalcev: tolmačenje | tolmači |
| 4102 | Storitve izvajalcev iz tujine (EU/tretje države) | tuji prevajalci in agencije; običajno reverse charge |
| 4110 | Podizvajalske platforme in prevajalska orodja | CAT/TMS licence, XTRF, strojno prevajanje |
| 4120 | Najemnine in poslovni prostori | najemnina pisarne, skupni stroški |
| 4130 | Komunikacije | telefon, internet, pošta |
| 4140 | Programska oprema in naročnine | SaaS, Microsoft/Google, domene, gostovanje |
| 4150 | Intelektualne storitve | računovodski servis, pravne storitve, revizija |
| 4160 | Marketing in oglaševanje | oglasi, spletna stran, sejmi |
| 4170 | Zavarovanja | premije |
| 4180 | Potni stroški in reprezentanca | prevozi, nastanitve, gostinstvo |
| 4190 | Drugi stroški storitev | karkoli, kar ne sodi drugam |
| 4000 | Material in pisarniški material | pisarniške potrebščine, drobni inventar |

## Terjatve in obveznosti
| Konto | Naziv | Uporaba |
|---|---|---|
| 160 | Terjatve za vstopni DDV | DDV z računa, če je odbiten |
| 220 | Obveznosti do dobaviteljev v državi | domači dobavitelji |
| 221 | Obveznosti do dobaviteljev v tujini | tuji dobavitelji |

## Odločitveno drevo (agent uporabi v tem vrstnem redu)
1. **Izvajalec iz XTRF (jezikovna storitev)** -> 4100 (ali 4101 tolmačenje). Poveži s projektom/jobom XTRF.
2. **Dobavitelj iz tujine** -> 4102, davčna obravnava = ZASTAVICA: možen reverse charge,
   servis potrdi in obračuna DDV.
3. **Izvajalec brez računa** (fizična oseba, podjemna/avtorska pogodba) -> NI račun:
   ZASTAVICA za servis (drugačna obravnava, dohodnina, prispevki).
4. **Programska oprema/naročnine** -> 4140. **Servis, odvetnik** -> 4150. **Marketing** -> 4160.
5. **Vse drugo** -> 4190 + zastavica "nejasen konto".
6. Pri mešanih računih (več postavk) razbij po postavkah in navedi konto za vsako.

## Profil izvajalcev (potrjeno): večinoma domači s.p. in d.o.o., nekaj tujih
- Domači s.p./d.o.o. = privzeta pot: 4100/4101 + 220 + 160, brez zastavice, če so podatki in DDV v redu.
- s.p. brez DDV je običajen (račun brez DDV s sklicem na oprostitev za male zavezance, npr. 94. člen ZDDV-1:
  preveri z servisom). Ni napaka, samo zabeleži "brez DDV, oprostitev" in preveri, da je sklic na računu.
- Tuj izvajalec = vedno ZASTAVICA (4102 + 221, reverse charge preveri servis); zbiraj jih v ločen razdelek paketa.
- Preveri tudi, da je domači dobavitelj aktiven in ima veljaven ID za DDV (če je zavezanec).

## DDV pravila za agenta (samo označevanje, ne odločanje)
- Izvajalec ni zavezanec za DDV (račun brez DDV, sklic na oprostitev): 160 = 0, označi.
- Račun z DDV: preveri stopnjo (22 %, 9,5 %, 5 %) in da DDV = neto x stopnja (toleranca 0,02 EUR).
- Vstopni DDV pri reprezentanci, osebnih avtomobilih ipd. je lahko omejen: ZASTAVICA.

## Odprto za servis (pošlji kot osnutek)
1. Ali sprejmejo te konte ali imajo svojo razdelitev (pošljejo naj svoj kontni načrt)?
2. Format uvoza v e-račune (stolpci CSV).
3. Obravnava reverse charge in fizičnih oseb.
