# xtrf-iphone-app

iPhone aplikacija (PWA – doda se na domači zaslon in deluje kot navadna app) s
3 okvirji:

- **Promet danes** – vsota `finance.totalAgreed` za projekte, katerih
  `actualStartDate` pade v ta dan, pretvorjena v EUR.
- **Promet ta teden** – enako za teden (od ponedeljka).
- **Promet YTD** – vsota `totalNetto` za izdane račune strank (status `SENT`,
  `dates.invoiceDate` letos), pretvorjena v EUR.

Enaka logika kot v [`xtrf-dashboard`](../xtrf-dashboard) (TV zaslon), le da
tu backend teče na **Cloudflare Workers** namesto na lokalnem računalniku, da
je dosegljiv s telefona od kjerkoli (WiFi ali mobilni podatki), ne le v
pisarniškem omrežju. XTRF API ključ je shranjen kot Worker secret in nikoli
ne pride do telefona/brskalnika – telefon kliče samo `/api/data` na tem
Workerju, Worker pa kliče XTRF.

## Arhitektura

- `src/index.ts` – Worker: servira statično PWA stran, `/api/data` vrne
  zadnje izračunane podatke iz KV (Workers KV), `scheduled` (cron vsakih 15
  min) izračuna sveže podatke in jih shrani v KV.
- `src/metrics.ts`, `src/xtrfClient.ts`, `src/cache.ts`, `src/dateUtils.ts` –
  logika izračuna (prilagojena verzija tiste iz `xtrf-dashboard`).
- `public/` – PWA (HTML/CSS/JS, manifest, ikone).

### YTD in omejitve Workers subrequestov

"Promet YTD" potrebuje podatke o vsakem letos izdanem računu (lahko nekaj
sto). Ker ima en klic Workerja omejeno število podrejenih HTTP klicev (50 na
Free planu, 1000 na Paid – glej
[Cloudflare docs](https://developers.cloudflare.com/workers/platform/limits/)),
se vsak račun, ko je enkrat prebran, **trajno predpomni v KV** (`invoice:<id>`
– zneski/datum/status izdanega računa se ne spreminjajo), `scheduled` pa ob
vsakem zagonu (privzeto vsakih 15 min) doda le omejeno število novih zapisov
(`MAX_INVOICES_PER_RUN` v `wrangler.jsonc`, privzeto 30). Ob prvi postavitvi
zato "dohitevanje" lahko traja nekaj ciklov (dokler `cachedInvoices` ne dohiti
`totalInvoiceCandidates` – aplikacija med tem prikaže "Posodabljam
zgodovino…" pod YTD okvirjem); kasneje se preverjajo le novo dodani računi,
kar je hitro. Če imaš Workers Paid plan, lahko `MAX_INVOICES_PER_RUN`
povečaš, da se prvo dohitevanje konča hitreje.

## Namestitev

Potreben je Cloudflare račun (Workers + Workers KV) in Node.js ≥ 18.

### Enkraten korak: KV namespace

KV namespace (predpomnilnik) je edina stvar, ki jo je treba ustvariti ročno
(Actions ga ne more ustvariti namesto tebe brez tvojega Cloudflare žetona) –
naredi to enkrat, z lokalno namestitvijo `wrangler` ali prek Cloudflare
nadzorne plošče (Workers & Pages → KV):

```bash
cd xtrf-iphone-app
npm install
npx wrangler login
npx wrangler kv namespace create CACHE
# -> v izpisu poišči "id": "..." in ga prepiši v wrangler.jsonc,
#    v kv_namespaces[0].id (namesto "REPLACE_WITH_KV_NAMESPACE_ID"),
#    nato commitaj in pushni to spremembo
```

### Priporočeno: deploy prek GitHub Actions

V repozitoriju je `.github/workflows/deploy-xtrf-iphone-app.yml`, ki ob vsakem
pushu v `xtrf-iphone-app/**` (ali ročno prek zavihka **Actions → Deploy
xtrf-iphone-app → Run workflow**) samodejno požene `wrangler deploy` **in**
nastavi/posodobi `XTRF_API_KEY` secret na Workerju – lokalni `wrangler`
sploh ni potreben za tekoče deploye.

V GitHub repozitoriju pod **Settings → Secrets and variables → Actions**
dodaj:

- `CLOUDFLARE_API_TOKEN` – Cloudflare API žeton z dovoljenjema *Workers
  Scripts: Edit* in *Workers KV Storage: Edit* (ustvariš ga na
  [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)).
- `CLOUDFLARE_ACCOUNT_ID` – najdeš ga na Cloudflare nadzorni plošči (Workers
  & Pages, desni rob).
- `XTRF_API_KEY` – XTRF API ključ; workflow ga ob vsakem zagonu prenese na
  Worker, zato ročni `wrangler secret put` ni potreben. Ko ključ zamenjaš, le
  posodobi ta GitHub secret in znova sproži workflow (push ali "Run
  workflow").

Po prvem uspešnem zagonu workflowa je aplikacija dosegljiva na
`https://xtrf-iphone-app.<tvoj-subdomain>.workers.dev` (natančen URL je tudi
v izpisu koraka "Deploy Worker" v Actions logu).

### Alternativa: ročni deploy iz lokalnega računalnika

```bash
npx wrangler secret put XTRF_API_KEY   # vnesi vrednost, ko vpraša
npm run types                          # generira worker-configuration.d.ts
npm run deploy                         # postavi Worker
```

### Lokalni razvoj

```bash
cp .dev.vars.example .dev.vars
# vpiši XTRF_API_KEY v .dev.vars
npm run dev
```

`wrangler dev` požene Worker lokalno (privzeto na `http://localhost:8787`) in
kliče pravi XTRF API ter pravi (ali lokalno simuliran, glede na wrangler
nastavitve) KV namespace. Cron se lokalno ne sproži sam – prvi obisk
`/api/data` (ali same aplikacije) sam izračuna podatke, če v KV še ni ničesar
(glej `src/index.ts`).

## Dodajanje na iPhone domači zaslon

1. Odpri objavljeni URL v Safariju na iPhoneu.
2. Tapni ikono "Deli" (kvadrat s puščico navzgor) → **Dodaj na domači zaslon**.
3. Aplikacija se doda kot ikona, ki se odpre v celozaslonskem načinu (brez
   Safari vrstice).

## Znane omejitve

- Enaka poenostavitev kot pri `xtrf-dashboard`: "Promet danes/teden" temelji
  na projektovem `actualStartDate`, ne na resničnem datumu kreiranja naloge
  (ta ni izpostavljen v javnem XTRF Home API) – glej opombo v
  [mcp-xtrf](../mcp-xtrf/README.md).
- Ikone (`public/icon-*.png`, `apple-touch-icon.png`) so trenutno generiran
  minimalističen placeholder (temen kvadrat z zlatim krogom) – zamenjaj z
  pravim Amidas app-icon designom, če želiš.
- Če je `XTRF_API_KEY` neveljaven, `/api/data` vrne `status: "error"` in
  aplikacija prikaže rdeč opozorilni pas (obdrži zadnje znane vrednosti, če
  obstajajo).
