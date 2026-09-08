<script setup lang="ts">
import { services } from "~/content/services";

const { t, te } = useI18n();
const localePath = useLocalePath();
const route = useRoute();

const service = services.find((s) => s.slug === route.params.slug);
if (!service) {
  throw createError({ statusCode: 404, statusMessage: "Service not found" });
}

const p = service.prefix;

useHead({
  title: te(`meta.${p}.title`) ? t(`meta.${p}.title`) : t(`${p}.h1`),
  meta: [{ name: "description", content: te(`meta.${p}.description`) ? t(`meta.${p}.description`) : "" }],
});

const features = computed(() => service.featureKeys.map((k) => t(k)));

const mockRows = computed(() =>
  service.mock.rows.map((row) => ({
    label: row.labelKey ? t(row.labelKey) : row.label ?? "",
    value: row.valueKey ? t(row.valueKey) : row.value ?? "",
    flag: row.flag,
  }))
);
</script>

<template>
  <div>
    <PageHero variant="page" :eyebrow="t(`${p}.crumb`)" :title="t(`${p}.h1`)" :lead="t(`${p}.lead`)">
      <template #crumb>
        <span class="service-crumb">
          <NuxtLink :to="localePath('/services')">{{ t("common.nav.services") }}</NuxtLink>
          {{ " " }}<span>{{ t(`${p}.crumb`) }}</span>
        </span>
      </template>
    </PageHero>

    <section class="detail-section">
      <div class="wrap detail-grid">
        <div class="detail-copy">
          <p>{{ t(`${p}.p1`) }}</p>
          <p>{{ t(`${p}.p2`) }}</p>
          <FeatureList :items="features" />
        </div>
        <div class="detail-visual" aria-hidden="true">
          <MockPanel
            :title="t(`${p}.mock.title`)"
            :rows="mockRows"
            :note="t(`${p}.mock.note`)"
            :tag="t(`${p}.mock.tag`)"
          />
        </div>
      </div>
    </section>

    <SubCta
      :title="t(`${p}.cta.h2`)"
      :lead="t(`${p}.cta.lead`)"
      :primary-label="t(`${p}.cta.btn1`)"
      :primary-to="localePath('/contact')"
      :secondary-label="t(`${p}.cta.btn2`)"
      :secondary-to="localePath('/services')"
    />
  </div>
</template>
