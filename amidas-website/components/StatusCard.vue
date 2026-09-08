<script setup lang="ts">
const { t } = useI18n();

const rows = computed(() => [
  { label: t("how.status.sourceReview"), value: t("how.status.complete"), tone: "ok" },
  { label: t("how.status.humanTranslation"), value: t("how.status.complete"), tone: "ok" },
  { label: t("how.status.termCheck"), value: t("how.status.complete"), tone: "ok" },
  { label: t("how.status.finalApproval"), value: t("how.status.awaiting"), tone: "warn" },
]);
</script>

<template>
  <div class="why-card">
    <div v-for="row in rows" :key="row.label" class="why-card-row">
      <span>{{ row.label }}</span>
      <span class="pill" :class="row.tone === 'ok' ? 'pill-ok' : 'pill-warn'">{{ row.value }}</span>
    </div>
  </div>
</template>
