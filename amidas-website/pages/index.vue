<script setup lang="ts">
const { t } = useI18n();
const localePath = useLocalePath();

useHead({
  title: t("meta.home.title"),
  meta: [{ name: "description", content: t("meta.home.description") }],
});

const mockRows = computed(() => [
  { label: t("home.mock.langPair.label"), value: "EN → DE" },
  { label: t("home.mock.termCheck.label"), value: t("home.mock.termCheck.value") },
  { label: t("home.mock.humanReview.label"), value: t("home.mock.humanReview.value"), flag: true },
]);

const problemCards = computed(() => [
  { icon: "🌍", title: t("home.problem.card1.title"), desc: t("home.problem.card1.desc") },
  { icon: "⏳", title: t("home.problem.card2.title"), desc: t("home.problem.card2.desc") },
  { icon: "🧩", title: t("home.problem.card3.title"), desc: t("home.problem.card3.desc") },
  { icon: "🤝", title: t("home.problem.card4.title"), desc: t("home.problem.card4.desc") },
]);

const serviceTeasers = computed(() => [
  {
    icon: "🌐",
    title: t("home.services.card1.title"),
    desc: t("home.services.card1.desc"),
    link: t("home.services.card1.link"),
    to: localePath("/services/translation-localization"),
  },
  {
    icon: "🎙️",
    title: t("home.services.card2.title"),
    desc: t("home.services.card2.desc"),
    link: t("home.services.card2.link"),
    to: localePath("/services/interpretation"),
  },
  {
    icon: "🤖",
    title: t("home.services.card3.title"),
    desc: t("home.services.card3.desc"),
    link: t("home.services.card3.link"),
    to: localePath("/services/ai-assisted-translation-qa"),
  },
]);

const faqItems = computed(() => [
  { q: t("home.faq.q1"), a: t("home.faq.a1") },
  { q: t("home.faq.q2"), a: t("home.faq.a2") },
  { q: t("home.faq.q3"), a: t("home.faq.a3") },
  { q: t("home.faq.q4"), a: t("home.faq.a4") },
  { q: t("home.faq.q5"), a: t("home.faq.a5") },
  { q: t("home.faq.q6"), a: t("home.faq.a6") },
]);
</script>

<template>
  <div>
    <PageHero
      variant="hero"
      :eyebrow="t('home.hero.eyebrow')"
      :title="t('home.hero.h1')"
      :lead="t('home.hero.lead')"
    >
      <template #actions>
        <div class="hero-actions">
          <NuxtLink class="btn btn-primary btn-lg" :to="localePath('/contact')">{{ t("home.hero.cta1") }}</NuxtLink>
          <NuxtLink class="btn btn-outline btn-lg" :to="localePath('/services')">{{ t("home.hero.cta2") }}</NuxtLink>
        </div>
      </template>
      <template #trust>
        <ul class="hero-trust">
          <li>{{ t("home.hero.trust1") }}</li>
          <li>{{ t("home.hero.trust2") }}</li>
          <li>{{ t("home.hero.trust3") }}</li>
        </ul>
      </template>
      <template #visual>
        <MockPanel
          :title="t('home.mock.title')"
          :rows="mockRows"
          :note="t('home.mock.note')"
          :tag="t('home.mock.tag')"
        />
      </template>
    </PageHero>

    <section class="problem">
      <div class="wrap">
        <h2>{{ t("home.problem.h2") }}</h2>
        <div class="problem-grid">
          <div v-for="card in problemCards" :key="card.title" class="problem-card">
            <div class="problem-icon" aria-hidden="true">{{ card.icon }}</div>
            <h3>{{ card.title }}</h3>
            <p>{{ card.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="teaser-section">
      <div class="wrap">
        <p class="eyebrow center">{{ t("home.services.eyebrow") }}</p>
        <h2 class="center">{{ t("home.services.h2") }}</h2>
        <p class="section-lead center">{{ t("home.services.lead") }}</p>

        <div class="teaser-grid">
          <div v-for="card in serviceTeasers" :key="card.title" class="teaser-card">
            <div class="teaser-icon" aria-hidden="true">{{ card.icon }}</div>
            <h3>{{ card.title }}</h3>
            <p>{{ card.desc }}</p>
            <NuxtLink class="teaser-link" :to="card.to">{{ card.link }}</NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <section class="mini-section">
      <div class="wrap">
        <p class="eyebrow center">{{ t("home.how.eyebrow") }}</p>
        <h2 class="center">{{ t("home.how.h2") }}</h2>
        <p class="section-lead center">{{ t("home.how.lead") }}</p>
        <div class="mini-section-actions">
          <NuxtLink class="btn btn-outline btn-lg" :to="localePath('/how-it-works')">{{ t("home.how.cta") }}</NuxtLink>
        </div>
      </div>
    </section>

    <section class="teaser-section">
      <div class="wrap">
        <p class="eyebrow center">{{ t("home.why.eyebrow") }}</p>
        <h2 class="center">{{ t("home.why.h2") }}</h2>
        <p class="section-lead center">{{ t("home.why.lead") }}</p>
        <div class="mini-section-actions">
          <NuxtLink class="btn btn-outline btn-lg" :to="localePath('/why-amidas')">{{ t("home.why.cta") }}</NuxtLink>
        </div>
      </div>
    </section>

    <section class="faq">
      <div class="wrap">
        <p class="eyebrow center">{{ t("home.faq.eyebrow") }}</p>
        <h2 class="center">{{ t("home.faq.h2") }}</h2>
        <FaqAccordion :items="faqItems" />
      </div>
    </section>

    <SubCta
      :title="t('home.cta.h2')"
      :lead="t('home.cta.lead')"
      :primary-label="t('home.cta.btn1')"
      :primary-to="localePath('/contact')"
      :secondary-label="t('home.cta.btn2')"
      secondary-href="mailto:hello@amidas.si"
    />
  </div>
</template>
