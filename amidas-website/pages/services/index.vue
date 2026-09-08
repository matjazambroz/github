<script setup lang="ts">
import { services } from "~/content/services";

const { t } = useI18n();
const localePath = useLocalePath();

useHead({
  title: t("meta.services.title"),
  meta: [{ name: "description", content: t("meta.services.description") }],
});

const cards = computed(() =>
  services.map((s, i) => ({
    slug: s.slug,
    icon: s.icon,
    title: t(`services.card${i + 1}.title`),
    desc: t(`services.card${i + 1}.desc`),
    link: t(`services.card${i + 1}.link`),
  }))
);
</script>

<template>
  <div>
    <PageHero variant="page" :eyebrow="t('services.hero.eyebrow')" :title="t('services.hero.h1')" :lead="t('services.hero.lead')" />

    <section class="solutions">
      <div class="wrap">
        <div class="solutions-grid">
          <div v-for="card in cards" :key="card.slug" class="solution-card">
            <div class="solution-icon" aria-hidden="true">{{ card.icon }}</div>
            <h3>{{ card.title }}</h3>
            <p>{{ card.desc }}</p>
            <NuxtLink class="teaser-link" :to="localePath(`/services/${card.slug}`)">{{ card.link }}</NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <SubCta
      :title="t('services.cta.h2')"
      :lead="t('services.cta.lead')"
      :primary-label="t('services.cta.btn1')"
      :primary-to="localePath('/contact')"
      :secondary-label="t('services.cta.btn2')"
      :secondary-to="localePath('/how-it-works')"
    />
  </div>
</template>
