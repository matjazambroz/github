<script setup lang="ts">
defineProps<{
  eyebrow: string;
  title: string;
  lead: string;
  /** "hero" = homepage dark hero with glow; "page" = smaller subpage hero */
  variant?: "hero" | "page";
}>();
</script>

<template>
  <section v-if="variant === 'hero'" class="hero">
    <div class="hero-glow" aria-hidden="true"></div>
    <div class="wrap hero-inner">
      <div class="hero-copy">
        <p class="eyebrow">{{ eyebrow }}</p>
        <h1>{{ title }}</h1>
        <p class="hero-lead">{{ lead }}</p>
        <slot name="actions" />
        <slot name="trust" />
      </div>
      <div class="hero-visual" aria-hidden="true">
        <slot name="visual" />
      </div>
    </div>
  </section>

  <section v-else class="page-hero">
    <div class="wrap page-hero-inner">
      <p class="eyebrow">
        <slot name="crumb">{{ eyebrow }}</slot>
      </p>
      <h1>{{ title }}</h1>
      <p class="hero-lead">{{ lead }}</p>
    </div>
  </section>
</template>
