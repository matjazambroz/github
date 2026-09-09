# Agent notes for amidas-website

Static marketing site — no build step, no package manager, no framework. Files are served as-is.

## Structure

- `index.html`, `contact.html`, `how-it-works.html`, `services.html`, `why-amidas.html` — pages, one per top-level nav link
- `css/styles.css` — single shared stylesheet for all pages
- `js/script.js` — mobile nav toggle, footer year, quote-request form handling (shared across pages)

## Working on this site

- Keep it dependency-free: no bundler, no npm install, no build command. Edit HTML/CSS/JS directly.
- Shared chrome (header nav, footer) is duplicated across the HTML files rather than templated — when changing nav links, footer links, or the copyright year logic, update every page, not just one.
- The "Request a quote" form (in `contact.html`, wired via `js/script.js`) has no backend — it shows a client-side confirmation only. Don't assume submissions are captured anywhere.
- Contact email placeholder is `hello@amidas.si`.
- Test changes with a plain static server (`python3 -m http.server 8080` from this directory) and check all five pages, not just the one edited, since nav/footer are shared markup.
