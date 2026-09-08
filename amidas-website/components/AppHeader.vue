<script setup lang="ts">
const { locale, locales, t } = useI18n();
const switchLocalePath = useSwitchLocalePath();
const localePath = useLocalePath();

const navOpen = ref(false);
function closeNav() {
  navOpen.value = false;
}

const availableLocales = computed(() => {
  const list = locales.value as Array<{ code: string; name?: string }>;
  const flags: Record<string, string> = { en: "🇬🇧", sl: "🇸🇮" };
  const labels: Record<string, string> = { en: "EN", sl: "SI" };
  return list.map((l) => ({ code: l.code, flag: flags[l.code] ?? "", label: labels[l.code] ?? l.code.toUpperCase() }));
});
</script>

<template>
  <header class="site-header">
    <div class="wrap header-inner">
      <NuxtLink class="brand" :to="localePath('/')">
        <img class="brand-logo" src="/logos/amidas-logo.svg" alt="Amidas" width="510" height="129" />
      </NuxtLink>

      <nav class="nav" :class="{ 'is-open': navOpen }" @click="closeNav">
        <NuxtLink :to="localePath('/services')" active-class="is-active">{{ t("common.nav.services") }}</NuxtLink>
        <NuxtLink :to="localePath('/how-it-works')" active-class="is-active">{{ t("common.nav.how") }}</NuxtLink>
        <NuxtLink :to="localePath('/why-amidas')" active-class="is-active">{{ t("common.nav.why") }}</NuxtLink>
        <NuxtLink :to="localePath('/contact')" active-class="is-active">{{ t("common.nav.contact") }}</NuxtLink>
      </nav>

      <div class="header-actions">
        <div class="lang-switch" role="group" aria-label="Language">
          <NuxtLink
            v-for="l in availableLocales"
            :key="l.code"
            class="lang-btn"
            :class="{ 'is-active': locale === l.code }"
            :to="switchLocalePath(l.code)"
            :aria-pressed="locale === l.code"
          >
            <span class="flag" aria-hidden="true">{{ l.flag }}</span>
            <span class="lang-label">{{ l.label }}</span>
          </NuxtLink>
        </div>
        <NuxtLink class="btn btn-ghost" :to="localePath('/contact')">{{ t("common.btn.contactUs") }}</NuxtLink>
        <NuxtLink class="btn btn-primary" :to="localePath('/contact')">{{ t("common.btn.quote") }}</NuxtLink>
        <button
          class="nav-toggle"
          aria-label="Toggle menu"
          :aria-expanded="navOpen"
          @click="navOpen = !navOpen"
        >
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </header>
</template>
