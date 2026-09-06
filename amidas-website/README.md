# Amidas Website

Marketing landing page positioning Amidas as a language communication partner — human
translators and interpreters supported by AI-assisted tools. A static site with no build step
or external dependencies beyond a Google Fonts import.

## Structure

- `index.html` — page markup
- `css/styles.css` — styling
- `js/script.js` — mobile nav toggle, footer year, quote-request form handling

## Running locally

Any static file server works, e.g.:

```bash
cd amidas-website
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080).

## Notes

- The "Request a quote" form has no backend wired up yet — it currently shows a confirmation
  message client-side. Wire `js/script.js`'s submit handler to a real endpoint (or a form
  service) before relying on it to collect leads.
- Contact email placeholder: `hello@amidas.si` — update if a different inbox should be used.
