# Changan Slovenija – pristajalna stran

Stran, gostovana kot Cloudflare Worker.

- `src/index.html` – celotna stran (HTML + CSS), `src/index.js` – Worker, ki jo streže
- `wrangler.jsonc` – konfiguracija Worker-ja

## Razvoj in objava
```
npm install
npm run dev      # lokalni predogled
npm run deploy   # objava na Cloudflare (potreben CLOUDFLARE_API_TOKEN)
```
Podatki prodajalca (ime, naslov, telefon, e-pošta) so začasni – zamenjaj jih v `src/index.html`.
