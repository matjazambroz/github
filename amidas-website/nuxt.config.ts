export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: { enabled: false },
  experimental: { appManifest: false },

  css: ["~/assets/css/main.css"],

  app: {
    head: {
      link: [
        { rel: "preconnect", href: "https://fonts.googleapis.com" },
        { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "" },
        {
          rel: "stylesheet",
          href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        },
      ],
    },
  },

  modules: ["@nuxtjs/i18n"],

  i18n: {
    restructureDir: "i18n",
    // A few keys (FAQ answer with a mailto link, the "why" list items) intentionally carry inline
    // HTML from trusted, statically-authored copy — not user input — so the bundler's HTML guard
    // is unnecessary here.
    compilation: { strictMessage: false },
    locales: [
      { code: "en", language: "en-US", name: "English", file: "en.json" },
      { code: "sl", language: "sl-SI", name: "Slovenščina", file: "sl.json" },
    ],
    defaultLocale: "en",
    strategy: "prefix_except_default",
    langDir: "locales",
    detectBrowserLanguage: false,
  },
});
