# mcp-xtrf

MCP (Model Context Protocol) strežnik za dostop do XTRF API-ja (npr. `xtrf.amidas.si`) iz Claude Code / Claude Desktop.

## Kaj počne

Strežnik se prijavi v XTRF Home API in Claude-u izpostavi njegove endpointe kot orodja (glej [Orodja](#orodja-mcp-tools)), tako da lahko Claude v pogovoru neposredno bere podatke iz XTRF-ja, namesto da bi uporabnik podatke ročno iskal po XTRF vmesniku. S tem je mogoče npr.:

- pregledovati projekte (posamezne, po ID-ju, po stranki/statusu ali tiste, spremenjene od danega datuma) in njihove joborodje,
- pregledovati stranke ("customers" v XTRF terminologiji),
- razreševati `currencyId` v berljivo valuto (EUR, USD, ...),
- pregledovati račune in plačila nanje — npr. "kateri računi so bili danes plačani" ali "kolikšen je dogovorjeni promet za danes",
- ali klicati poljuben drug XTRF endpoint prek generičnega `xtrf_request` orodja, če za njega (še) ni namenskega orodja.

Ni spletna aplikacija ali API strežnik za zunanje uporabnike — je lokalni proces (stdio), ki ga zažene Claude Code/Desktop in komunicira izključno z enim XTRF instance, konfiguriranim prek okoljskih spremenljivk.

## Stanje

Amidas uporablja **XTRF Home API**. Od uporabnika smo dobili polno OpenAPI (Swagger) specifikacijo instance (server URL `https://xtrf.amidas.si/home-api`, avtentikacija `X-AUTH-ACCESS-TOKEN`) — skrajšan povzetek je v [`docs/openapi.json`](docs/openapi.json) (`_endpoints_used_by_mcp_xtrf`), poln spec pa je vedno na voljo na `https://xtrf.amidas.si/home-api/openapi.json`.

**Preverjeno proti pravi instanci** (dejansko poklicano, vrnilo pravi zapis):

- `GET /home-api/projects/{id}`, npr. `GET https://xtrf.amidas.si/home-api/projects/86652`
- `GET /home-api/customers/{id}`, npr. `GET https://xtrf.amidas.si/home-api/customers/7` — **pomembno:** "stranka"/"client" je v XTRF Home API imenovan **`customer`**, ne `client` (`/clients/{id}` vrne 404). `xtrf_get_client`/`xtrf_list_clients` zato interno kličeta `/customers`.
- `GET /home-api/projects/ids?updatedSince=...`

Ugotovitve iz OpenAPI specifikacije:
- Bazna pot: `/home-api` — brez `/v2` v poti.
- Avtentikacija: header `X-AUTH-ACCESS-TOKEN` (apiKey), surov token brez predpone (npr. brez `Bearer `).
- `Accept` header za odgovore mora biti verzionirani vendor media type, ne navaden `application/json` — `application/vnd.xtrf-v1+json;charset=UTF-8` (`XTRF_ACCEPT_HEADER`).
- `Content-Type` za telo pri POST/PUT/PATCH je navaden `application/json;charset=UTF-8` (`XTRF_CONTENT_TYPE_HEADER`) — **ni** enak `Accept` headerju.
- **`GET /projects` (seznam vseh projektov) ne obstaja** — `/projects` podpira samo `POST` (ustvarjanje). Za seznam projektov uporabi `xtrf_list_project_ids` + `xtrf_get_project` za vsak ID, ali `/browser` endpoint (potrebuje shranjen `viewId` v XTRF-ju, ni implementirano kot posebno orodje).
- **Splošen `GET /jobs` (seznam vseh jobov) prav tako ne obstaja.** Na voljo sta le `GET /jobs/{jobId}` (posamezen Classic job) in `GET /v2/projects/{projectId}/jobs` (vsi jobi znotraj enega Smart projekta).

To je zdaj privzeta nastavitev (glej `.env.example`).

Načina `classic_login` (prijava z uporabniškim imenom/geslom) in `oauth2` sta v kodi ohranjena kot alternativi, če bi jih kdaj potreboval kak drug XTRF endpoint.

## Namestitev

```bash
cd mcp-xtrf
npm install
cp .env.example .env
# uredi .env: vpiši XTRF_BASE_URL, XTRF_API_KEY (ali OAuth2 podatke), XTRF_API_BASE_PATH
npm run build
```

## Avtentikacija

Podprti so trije načini, nastavljivi z `XTRF_AUTH_MODE`:

- **`apikey`** (privzeto) — statičen token v HTTP headerju `X-AUTH-ACCESS-TOKEN` (`XTRF_API_KEY_HEADER`), brez predpone (`XTRF_API_KEY_PREFIX` privzeto prazno) — po Swagger dokumentaciji na `/api-doc#/home-api/`.
- **`classic_login`** — prijava z uporabniškim imenom/geslom (`XTRF_USERNAME`, `XTRF_PASSWORD`) na `XTRF_LOGIN_URL` (privzeto `{XTRF_BASE_URL}{XTRF_API_BASE_PATH}/session`). Pridobljeni session token se pošilja v headerju `XTRF_SESSION_HEADER` (privzeto `X-AUTH-ACCESS-TOKEN`) in predpomni ~25 minut.
- **`oauth2`** — OAuth2 `client_credentials` flow. Potrebuje `XTRF_CLIENT_ID`, `XTRF_CLIENT_SECRET` in `XTRF_TOKEN_URL`. Token se predpomni do izteka.

## Orodja (MCP tools)

- `xtrf_request` — generičen klic na poljuben endpoint (`method`, `path`, `query`, `body`). Uporabi to, če specifično orodje ne obstaja ali če pot ne ustreza.
- `xtrf_list_project_ids` — `GET /projects/ids` (preverjeno; sprejme `updatedSince` kot datum `YYYY-MM-DD`, ki se pretvori v epoch ms za polnoč tega dne v časovnem pasu `XTRF_TIMEZONE`, privzeto `Europe/Ljubljana`)
- `xtrf_get_project` — `GET /projects/{projectId}` (preverjeno)
- `xtrf_search_projects` — poišče projekte po stranki (`customerId`) in/ali statusu (`status`), npr. "odprti projekti za stranko X". API nima neposrednega iskalnega endpointa, zato orodje najprej pridobi ID-je (`GET /projects/ids`, po možnosti omejeno z `updatedSince`) in nato vsakega posebej preveri (`GET /projects/{id}`), filtrirano na strani odjemalca. Za hitrost in popolnost rezultatov vedno navedi `updatedSince`, kadar je mogoče.
- `xtrf_get_job` — `GET /jobs/{jobId}` (posamezen Classic job)
- `xtrf_list_project_jobs` — `GET /v2/projects/{projectId}/jobs` (vsi jobi enega Smart projekta — edini "seznam jobov" endpoint, ki obstaja)
- `xtrf_list_clients` — `GET /customers` (preverjeno; sprejme `updatedSince`, `excludeErased`)
- `xtrf_get_client` — `GET /customers/{clientId}` (preverjeno)
- `xtrf_list_currencies` — `GET /dictionaries/currency/active` ali `/all`. Namenskega `/currencies` endpointa ni, zato uporablja generični slovarski (`dictionaries`) endpoint iz OpenAPI speca.
- `xtrf_get_currency` — `GET /dictionaries/currency/{id}`, za razrešitev polja `currencyId` (npr. na projektu/stranki) v ISO kodo/simbol.
- `xtrf_list_invoice_ids` — `GET /accounting/customers/invoices/ids` (sprejme `updatedSince`)
- `xtrf_get_invoice` — `GET /accounting/customers/invoices/{invoiceId}` (status, zneski, `currencyId`, datumi)
- `xtrf_get_invoice_payments` — `GET /accounting/customers/invoices/{invoiceId}/payments` (znesek, `paymentDate`, `paymentMethodId` na plačilo)
- `xtrf_search_paid_invoices` — poišče plačila računov na določen dan (npr. "kaj je bilo plačano danes"). API nima endpointa za "plačila po datumu", zato orodje najprej pridobi kandidate (`GET /accounting/customers/invoices/ids?updatedSince=<dan>`), nato za vsakega preveri `.../payments` in obdrži samo tiste s `paymentDate` na ta dan; za zadetke še pridobi `GET .../{invoiceId}` za `currencyId`.

## Povezava s Claude Code

Dodaj v konfiguracijo MCP strežnikov (`claude mcp add` ali `.mcp.json`):

```json
{
  "mcpServers": {
    "xtrf": {
      "command": "node",
      "args": ["/pot/do/repozitorija/mcp-xtrf/dist/index.js"],
      "env": {
        "XTRF_BASE_URL": "https://xtrf.amidas.si",
        "XTRF_API_BASE_PATH": "/home-api",
        "XTRF_AUTH_MODE": "apikey",
        "XTRF_API_KEY": "..."
      }
    }
  }
}
```

**Ključa nikoli ne commitaj v repozitorij** — nastavi ga lokalno prek `.env` ali `env` bloka v MCP konfiguraciji, ki ni v git-u.
