# xtrf-dashboard

Samostojna aplikacija (brez Claude Code / MCP), ki kliče XTRF API neposredno in prikazuje ključne finančne kazalnike na lokalni spletni strani. Zasnovana za prikaz na pisarniškem TV-ju (velika, temna postavitev, samodejno osvežuje brez interakcije).

## Kazalniki

**Hitri cikel (privzeto vsakih 15 min, `REFRESH_MINUTES`):**
- **Promet danes / ta teden** — vsota `finance.totalAgreed` za projekte, katerih `actualStartDate` pade v ta dan/teden (teden od ponedeljka). Tedenski znesek je pretvorjen v en skupni EUR znesek (XTRF-jev tečaj).
- **Plačani računi danes / ta teden** — vsota dejansko prejetih plačil v tem obdobju, pretvorjena v EUR.

**Počasni cikel (privzeto vsakih 60 min, `YTD_REFRESH_MINUTES`, keširano po ID-ju računa):**
- **Promet YTD** — vsota `totalNetto` za račune strank, izdane letos (`dates.invoiceDate`, status `SENT`), pretvorjena v EUR, s primerjavo do istega dne lani.
- **Stroški YTD** — enako za račune izvajalcev (`dates.finalDate`).
- **Plačani računi YTD** — od zgornjega, samo tisti, ki so v celoti plačani.
- **Plačani stroški YTD** — enako, filtrirano po `paymentStatus: FULLY_PAID`.

Vsi YTD izračuni uporabljajo trajen lokalen predpomnilnik (`data/*.json`, ni v git-u) — osnovni podatki posameznega računa se prenesejo samo enkrat.

## Namestitev in zagon

```bash
cd xtrf-dashboard
cp .env.example .env
# uredi .env: vpiši XTRF_API_KEY (in po potrebi ostale nastavitve)
npm start
```

Odpri [http://localhost:4173](http://localhost:4173) v brskalniku.

Ni potrebe po `npm install` — aplikacija nima zunanjih odvisnosti (uporablja vgrajen Node `http` in `fetch`, Node ≥ 18; `--env-file` zahteva Node ≥ 20.6).

## Prikaz na pisarniškem TV-ju (Chromecast)

1. Zaženi aplikacijo na računalniku, ki bo ostal prižgan (`npm start`).
2. V Chrome odpri `http://localhost:4173`, pojdi v celozaslonski način (F11 / Cmd+Ctrl+F).
3. Chrome meni (⋮) → **Cast...** → izberi TV/Chromecast napravo → **Cast tab**.

Ker gre za navadno spletno stran, cast deluje enako kot za katerokoli drugo stran — ni potrebne dodatne nastavitve v kodi.

## Samodejni zagon ob prijavi (macOS, izbirno)

Če želiš, da se strežnik zažene sam ob zagonu Mac-a (da ne skrbiš, če se terminal zapre), lahko nastavimo `launchd` servis — povej, če to želiš, in ga dodam.

## Konfiguracija (.env)

Glej [`.env.example`](.env.example) — `XTRF_API_KEY` je edina obvezna nastavitev poleg privzetih. `REFRESH_MINUTES` (privzeto 15) in `YTD_REFRESH_MINUTES` (privzeto 60) določata pogostost osveževanja, `PORT` (privzeto 4173) lokalna vrata strežnika.

## Znane omejitve

- Prikazani dnevni/tedenski "Promet" ni enak XTRF-jevemu internemu poročilu "MA - danes vnešeni projekti" (Task Total Agreed, filtrirano po datumu kreiranja projekta) — glej opombo v [mcp-xtrf](../mcp-xtrf/README.md). To je namerna, sprejeta poenostavitev (project-level `actualStartDate` namesto task-level datuma kreiranja, ki ni izpostavljen v javnem XTRF Home API). YTD kazalniki (ki temeljijo na računih, ne projektih) te omejitve nimajo, ker računi imajo pravi `invoiceDate`/`finalDate`.
- Če je `XTRF_API_KEY` neveljaven, se na strani prikaže rdeč opozorilni pas; strežnik ob naslednjem ciklu samodejno poskusi znova.
- Ob prvem zagonu (ali po spremembi filtrov, ki zahteva dodatno polje v predpomnilniku) lahko YTD izračun traja nekaj minut, ker mora enkrat preveriti vsak račun; kasneje je hiter zaradi predpomnilnika.
