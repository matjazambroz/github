# Amidas Website

Marketing site for Amidas — a language communication partner offering translation, localization,
interpretation, and AI-assisted language services. Built with [Nuxt 3](https://nuxt.com) and
[@nuxtjs/i18n](https://i18n.nuxtjs.org/).

## Structure

- `pages/` — file-based routes: home, services (overview + `[slug]` detail pages), how-it-works,
  why-amidas, contact
- `components/` — shared UI: header/footer, hero, mock UI panels, feature lists, FAQ accordion,
  the bottom CTA banner
- `content/services.ts` — the registry of the six services (slug, icon, i18n key prefix, and the
  mock-panel row data for each service's detail page)
- `i18n/locales/{en,sl}.json` — full English and Slovenian copy, including page metadata (270+
  keys, kept in parity between the two languages)
- `assets/css/main.css` — the site's design system (design tokens, layout, components)
- `public/logos/` — the Amidas wordmark (dark-text variant for light backgrounds, plus the
  original white version for dark contexts)

## Languages

English is served at the site root (`/`, `/services`, …); Slovenian is served under `/sl/`
(`/sl/`, `/sl/storitve`… no — routes keep their English slugs under `/sl/`, e.g. `/sl/services`).
Both locales are real, indexable URLs (not a client-side toggle), so Slovenian content is
crawlable and shareable on its own link.

## Running locally

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Building

```bash
npm run build      # Node server output (npm run preview to try it)
npm run generate   # fully static output in .output/public, for static hosting
```

## Notes

- The "Request a quote" form has no backend wired up yet — it shows a client-side confirmation
  message only. Wire `pages/contact.vue`'s `onSubmit` to a real endpoint before relying on it to
  collect leads.
- Contact email placeholder: `hello@amidas.si`.
