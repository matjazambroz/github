<script setup lang="ts">
const { t } = useI18n();
const localePath = useLocalePath();

useHead({
  title: t("meta.why.title"),
  meta: [{ name: "description", content: t("meta.why.description") }],
});

const listItems = computed(() => [t("why.list.item1"), t("why.list.item2"), t("why.list.item3"), t("why.list.item4")]);
</script>

<template>
  <div>
    <PageHero variant="page" :eyebrow="t('why.hero.eyebrow')" :title="t('why.hero.h1')" :lead="t('why.hero.lead')" />

    <section class="why">
      <div class="wrap why-inner">
        <div class="why-copy">
          <ul class="why-list">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <li v-for="(item, i) in listItems" :key="i" v-html="item"></li>
          </ul>
        </div>
        <div class="why-visual" aria-hidden="true">
          <StatusCard />
        </div>
      </div>
    </section>

    <SubCta
      :title="t('why.cta.h2')"
      :lead="t('why.cta.lead')"
      :primary-label="t('why.cta.btn1')"
      :primary-to="localePath('/contact')"
      :secondary-label="t('why.cta.btn2')"
      :secondary-to="localePath('/services')"
    />
  </div>
</template>
