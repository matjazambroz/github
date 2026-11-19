# Changan Slovenija – pristajalna stran

Statična stran, gostovana na Cloudflare Workers (static assets).

- `public/index.html` – celotna stran (HTML + CSS, brez odvisnosti)
- `wrangler.jsonc` – konfiguracija Worker-ja

## Razvoj in objava
```
npm install
npm run dev      # lokalni predogled
npm run deploy   # objava na Cloudflare (potreben CLOUDFLARE_API_TOKEN)
```
Podatki prodajalca (ime, naslov, telefon, e-pošta) so začasni – zamenjaj jih v `public/index.html`.
