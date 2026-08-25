# mcp-xtrf

MCP (Model Context Protocol) strežnik za dostop do XTRF API-ja (npr. `xtrf.amidas.si`) iz Claude Code / Claude Desktop.

## Stanje

Amidas uporablja **XTRF Home API**, dokumentiran na `https://xtrf.amidas.si/api-doc#/home-api/`. Avtentikacija je potrjena po Swagger dokumentaciji: header `X-AUTH-ACCESS-TOKEN` (apiKey), surov token brez predpone (npr. brez `Bearer `) — to je zdaj privzeta nastavitev (`XTRF_AUTH_MODE=apikey`, `XTRF_API_KEY_HEADER=X-AUTH-ACCESS-TOKEN`, `XTRF_API_KEY_PREFIX=` prazno).

Ker iz tega razvojnega okolja ni bilo mogoče doseči `xtrf.amidas.si` (omrežje je blokiralo dostop), poti posameznih endpointov (`/projects`, `/clients`, `/jobs`, ...) in oblika njihovih odgovorov niso preverjene proti dejanski dokumentaciji na `/api-doc`. Pred prvo uporabo:

1. V `/api-doc#/home-api/` preveri točne poti in parametre za operacije, ki jih potrebuješ.
2. Če se razlikujejo od privzetih v `xtrf_list_projects`/`xtrf_get_project`/`xtrf_list_jobs`/`xtrf_list_clients`/`xtrf_get_client`, uporabi generično orodje `xtrf_request`, ki sprejme poljubno pot/metodo — ni ti treba čakati, da popravim kodo.

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
- `xtrf_list_projects` — `GET /projects`
- `xtrf_get_project` — `GET /projects/{projectId}`
- `xtrf_list_jobs` — `GET /jobs` ali `GET /projects/{projectId}/jobs`
- `xtrf_list_clients` — `GET /clients`
- `xtrf_get_client` — `GET /clients/{clientId}`

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
        "XTRF_API_BASE_PATH": "/home-api/v2",
        "XTRF_AUTH_MODE": "apikey",
        "XTRF_API_KEY": "..."
      }
    }
  }
}
```

**Ključa nikoli ne commitaj v repozitorij** — nastavi ga lokalno prek `.env` ali `env` bloka v MCP konfiguraciji, ki ni v git-u.
