<script setup lang="ts">
defineProps<{ items: string[] }>();
</script>

<template>
  <ul class="feature-list">
    <li v-for="item in items" :key="item">
      <span class="feature-check" aria-hidden="true">✓</span>
      <span>{{ item }}</span>
    </li>
  </ul>
</template>
