<script setup lang="ts">
const { t } = useI18n();
const localePath = useLocalePath();

useHead({
  title: t("meta.how.title"),
  meta: [{ name: "description", content: t("meta.how.description") }],
});

const steps = computed(() => [
  { num: "01", title: t("how.step1.title"), desc: t("how.step1.desc") },
  { num: "02", title: t("how.step2.title"), desc: t("how.step2.desc") },
  { num: "03", title: t("how.step3.title"), desc: t("how.step3.desc") },
]);
</script>

<template>
  <div>
    <PageHero variant="page" :eyebrow="t('how.hero.eyebrow')" :title="t('how.hero.h1')" :lead="t('how.hero.lead')" />

    <section class="how">
      <div class="wrap">
        <div class="how-steps">
          <div v-for="step in steps" :key="step.num" class="how-step">
            <div class="how-number">{{ step.num }}</div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="why-visual-standalone">
      <div class="wrap">
        <StatusCard />
      </div>
    </section>

    <SubCta
      :title="t('how.cta.h2')"
      :lead="t('how.cta.lead')"
      :primary-label="t('how.cta.btn1')"
      :primary-to="localePath('/contact')"
      :secondary-label="t('how.cta.btn2')"
      :secondary-to="localePath('/services')"
    />
  </div>
</template>
