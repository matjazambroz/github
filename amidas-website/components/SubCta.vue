<script setup lang="ts">
defineProps<{
  title: string;
  lead: string;
  primaryLabel: string;
  primaryTo: string;
  secondaryLabel: string;
  secondaryTo?: string;
  secondaryHref?: string;
}>();
</script>

<template>
  <section class="subcta">
    <div class="wrap">
      <h2>{{ title }}</h2>
      <p>{{ lead }}</p>
      <div class="subcta-actions">
        <NuxtLink class="btn btn-primary btn-lg" :to="primaryTo">{{ primaryLabel }}</NuxtLink>
        <NuxtLink v-if="secondaryTo" class="btn btn-outline btn-lg" :to="secondaryTo">{{ secondaryLabel }}</NuxtLink>
        <a v-else-if="secondaryHref" class="btn btn-outline btn-lg" :href="secondaryHref">{{ secondaryLabel }}</a>
      </div>
    </div>
  </section>
</template>
