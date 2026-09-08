<script setup lang="ts">
defineProps<{ items: Array<{ q: string; a: string }> }>();
</script>

<template>
  <div class="faq-list">
    <details v-for="item in items" :key="item.q" class="faq-item">
      <summary>{{ item.q }}</summary>
      <!-- eslint-disable-next-line vue/no-v-html -->
      <p v-html="item.a"></p>
    </details>
  </div>
</template>
