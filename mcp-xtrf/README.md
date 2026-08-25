# mcp-xtrf

MCP (Model Context Protocol) strežnik za dostop do XTRF API-ja (npr. `xtrf.amidas.si`) iz Claude Code / Claude Desktop.

## Stanje

Amidas uporablja **XTRF Home API**, dokumentiran na `https://xtrf.amidas.si/api-doc#/home-api/`, z avtentikacijo prek statičnega tokena (privzeti način `apikey`, glej spodaj). Ker iz tega razvojnega okolja ni bilo mogoče doseči `xtrf.amidas.si` (omrežje je blokiralo dostop), imena headerja in oblike tokena (`XTRF_API_KEY_HEADER=Authorization`, `XTRF_API_KEY_PREFIX=Bearer `) nisem mogel preveriti proti dejanski dokumentaciji na `/api-doc` — gre za razumno privzeto vrednost. Pred prvo uporabo:

1. Odpri `https://xtrf.amidas.si/api-doc#/home-api/` in preveri, v katerem headerju in obliki API pričakuje token (npr. `Authorization: Bearer <token>` vs. drug header brez prefiksa).
2. Prilagodi `.env` (`XTRF_API_KEY_HEADER`, `XTRF_API_KEY_PREFIX`, `XTRF_API_KEY`) glede na to.
3. Če se poti endpointov (`/projects`, `/clients`, `/jobs`, ...) razlikujejo od privzetih, uporabi generično orodje `xtrf_request`, ki sprejme poljubno pot/metodo — ni ti treba čakati, da popravim kodo.

Načina `classic_login` (prijava z uporabniškim imenom/geslom) in `oauth2` sta v kodi ohranjena kot alternativi, če se izkaže, da ju instanca dejansko potrebuje namesto statičnega tokena.

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

- **`apikey`** (privzeto) — statičen token v HTTP headerju. Ime headerja nastaviš z `XTRF_API_KEY_HEADER` (privzeto `Authorization`), pred token pa se doda `XTRF_API_KEY_PREFIX` (privzeto `Bearer `; nastavi na prazen niz, če API pričakuje surov token brez predpone).
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
        "XTRF_API_KEY": "...",
        "XTRF_API_KEY_HEADER": "Authorization",
        "XTRF_API_KEY_PREFIX": "Bearer "
      }
    }
  }
}
```

**Ključa nikoli ne commitaj v repozitorij** — nastavi ga lokalno prek `.env` ali `env` bloka v MCP konfiguraciji, ki ni v git-u.
