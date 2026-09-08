<script setup lang="ts">
const { t } = useI18n();
const localePath = useLocalePath();
const year = new Date().getFullYear();
</script>

<template>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-brand">
        <img class="brand-logo" src="/logos/amidas-logo.svg" alt="Amidas" width="510" height="129" />
      </div>
      <nav class="footer-nav">
        <NuxtLink :to="localePath('/services')">{{ t("common.nav.services") }}</NuxtLink>
        <NuxtLink :to="localePath('/how-it-works')">{{ t("common.nav.how") }}</NuxtLink>
        <NuxtLink :to="localePath('/why-amidas')">{{ t("common.nav.why") }}</NuxtLink>
        <NuxtLink :to="localePath('/contact')">{{ t("common.nav.contact") }}</NuxtLink>
      </nav>
      <p class="footer-copy">&copy; {{ year }} Amidas. {{ t("common.footer.rights") }}</p>
    </div>
  </footer>
</template>
