# mcp-xtrf

MCP (Model Context Protocol) strežnik za dostop do XTRF API-ja (npr. `xtrf.amidas.si`) iz Claude Code / Claude Desktop.

## Stanje

Amidas uporablja **XTRF Home API**, dokumentiran na `https://xtrf.amidas.si/api-doc#/home-api/`.

**Preverjeno proti pravi instanci** (dejansko poklicano, vrnilo pravi zapis):

- `GET /home-api/projects/{id}`, npr. `GET https://xtrf.amidas.si/home-api/projects/86652`
- `GET /home-api/customers/{id}`, npr. `GET https://xtrf.amidas.si/home-api/customers/7` — **pomembno:** "stranka"/"client" je v XTRF Home API imenovan **`customer`**, ne `client` (`/clients/{id}` vrne 404). `xtrf_get_client`/`xtrf_list_clients` zato interno kličeta `/customers`.

Skupne ugotovitve:
- Bazna pot: `/home-api` — brez `/v2` v poti.
- Avtentikacija: header `X-AUTH-ACCESS-TOKEN` (apiKey), surov token brez predpone (npr. brez `Bearer `).
- `Accept` header mora biti verzionirani vendor media type, ne navaden `application/json` — `application/vnd.xtrf-v1+json;charset=UTF-8` (`XTRF_ACCEPT_HEADER`). Isti media type se uporabi tudi kot `Content-Type` pri POST/PUT/PATCH.

To je zdaj privzeta nastavitev (glej `.env.example`). Poti za `xtrf_list_projects` in `xtrf_list_jobs` (`/projects`, `/jobs`) so še vedno neverificirane predpostavke — preveri jih v `/api-doc#/home-api/`, preden jih zaupaš. Če se razlikujejo, uporabi generično orodje `xtrf_request`, ki sprejme poljubno pot/metodo — ni ti treba čakati, da popravim kodo.

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
- `xtrf_list_project_ids` — `GET /projects/ids` (preverjeno; sprejme `updatedSince` kot datum `YYYY-MM-DD`, ki se pretvori v epoch ms za polnoč tega dne v časovnem pasu `XTRF_TIMEZONE`, privzeto `Europe/Ljubljana`)
- `xtrf_get_project` — `GET /projects/{projectId}` (preverjeno)
- `xtrf_list_jobs` — `GET /jobs` ali `GET /projects/{projectId}/jobs`
- `xtrf_list_clients` — `GET /customers` (preverjeno)
- `xtrf_get_client` — `GET /customers/{clientId}` (preverjeno)

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
