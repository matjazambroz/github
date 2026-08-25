# mcp-xtrf

MCP (Model Context Protocol) strežnik za dostop do XTRF API-ja (npr. `xtrf.amidas.si`) iz Claude Code / Claude Desktop.

## Stanje

Ker iz tega razvojnega okolja ni bilo mogoče doseči `xtrf.amidas.si` (omrežje je blokiralo dostop) niti dobiti API dokumentacije, so poti endpointov (`/projects`, `/clients`, `/jobs`, ...) in avtentikacijska metoda **najboljša ocena na podlagi običajne XTRF Home REST API v2 konvencije** — ne preverjena implementacija. Pred prvo uporabo:

1. Preveri v XTRF admin panelu (Settings → API / Integrations) točno bazno pot API-ja (`XTRF_API_BASE_PATH`) in način avtentikacije.
2. Prilagodi `.env` glede na to.
3. Če se poti endpointov razlikujejo, uporabi generično orodje `xtrf_request`, ki sprejme poljubno pot/metodo — ni ti treba čakati, da popravim kodo.

## Namestitev

```bash
cd mcp-xtrf
npm install
cp .env.example .env
# uredi .env: vpiši XTRF_BASE_URL, XTRF_API_KEY (ali OAuth2 podatke), XTRF_API_BASE_PATH
npm run build
```

## Avtentikacija

Podprta sta dva načina, nastavljiva z `XTRF_AUTH_MODE`:

- **`apikey`** (privzeto) — statičen ključ v HTTP headerju. Ime headerja nastaviš z `XTRF_API_KEY_HEADER` (privzeto `X-API-KEY`; nekatere starejše XTRF namestitve uporabljajo `X-AUTH-ACCESS-TOKEN`).
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
        "XTRF_API_KEY": "...",
        "XTRF_API_KEY_HEADER": "X-API-KEY"
      }
    }
  }
}
```

**Ključa nikoli ne commitaj v repozitorij** — nastavi ga lokalno prek `.env` ali `env` bloka v MCP konfiguraciji, ki ni v git-u.
