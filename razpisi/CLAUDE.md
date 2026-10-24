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

Nadzor šteje stroške vseh sej v mapi `razpisi`. Za štetje samo od začetka dela na razpisu zaženi z `NADZOR_OD=razpis` (PowerShell: `$env:NADZOR_OD="razpis"; python nadzor.py <razpis>`).

## Izvoz v Word in PDF
`python orodja/izvozi.py <ime-razpisa>` pretvori `izhod/<razpis>/*.md` v `.docx` in `.pdf` (PDF le, če je nameščen Word ali LibreOffice). Potrebuje `pip install python-docx`. Skill ga požene kot zadnji korak.
