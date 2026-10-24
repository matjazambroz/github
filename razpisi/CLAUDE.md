# Razpisi – priprava prijav

Komunikacija je v slovenščini; angleški izrazi samo, kadar prevod ni mogoč.

## Struktura
- `vhod/<razpis>/` – razpisna dokumentacija (PDF, DOCX) enega razpisa
- `viri/` – reference podjetja, življenjepisi, cenik, standardni odgovori
- `izhod/<razpis>/` – generirani dokumenti: `zahteve.md`, `osnutek.md`, `ponudba.md`

## Potek (orkestracija)
1. `analitik-razpisa` – iz dokumentacije izlušči zahteve, merila, roke, obrazce → `izhod/<razpis>/zahteve.md`
2. `pisec-prijave` – po zahtevah in virih napiše osnutek odgovorov → `osnutek.md`
3. `kalkulant` – pripravi cenovno ponudbo → `ponudba.md`
4. `pregledovalec` – preveri skladnost z merili in zahtevami; vrne seznam vrzeli

Uporabi skill `priprava-prijave` za celoten potek.

## Pravila
- Nikoli si ne izmišljaj referenc ali številk; manjkajoče podatke označi z `[MANJKA: ...]`.
- Vsaka trditev v osnutku naj ima vir v `viri/`.
- Končnih prijav ne oddajaj in ne pošiljaj brez izrecne potrditve uporabnika.

## Nadzor v živo
`python nadzor/nadzor.py <ime-razpisa>` odpre lokalno stran (http://localhost:8765) s stanjem korakov, datotekami in zadnjimi dogodki agentov. Zaženi jo v drugem oknu terminala; samo bere datoteke.

Nadzor šteje stroške vseh sej v mapi `razpisi`. Gumb »Ponastavi stroške« na strani (ali zagon z `--ponastavi`) začne šteti znova od zdaj; zapisov sej ne briše. Za štetje samo od začetka dela na razpisu zaženi z `NADZOR_OD=razpis` (PowerShell: `$env:NADZOR_OD="razpis"; python nadzor.py <razpis>`).

## Izpolnjeni obrazci v izvirni obliki (Word, Excel, PDF)
Končni dokumenti so **izvirni razpisni obrazci**, izpolnjeni v kopiji (`izhod/<razpis>/obrazci/`), z vso izvirno obliko: glave, noge, oštevilčenje, tip in velikost pisave. Agent `izpolnjevalec-obrazcev` jih izpolni, `python orodja/preveri_obliko.py <izvirnik> <izpolnjeno>` preveri, da se oblika ni spremenila, `python orodja/izvozi.py <razpis>` naredi PDF. Izvirnikov v `vhod/` nikoli ne spreminjaj.
`.md` datoteke (`zahteve`, `osnutek`, `ponudba`, `pregled`) so delovni material; z `--md` jih izvozi v Word s splošno obliko, ki ni izvirna oblika razpisa.
