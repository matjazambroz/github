<script setup lang="ts">
defineProps<{
  title: string;
  rows: Array<{ label: string; value: string; flag?: boolean }>;
  note: string;
  tag: string;
}>();
</script>

<template>
  <div class="mock-window">
    <div class="mock-titlebar">
      <span class="dot dot-r"></span><span class="dot dot-y"></span><span class="dot dot-g"></span>
      <span class="mock-title">{{ title }}</span>
    </div>
    <div class="mock-body">
      <div v-for="row in rows" :key="row.label" class="mock-row">
        <span class="mock-label">{{ row.label }}</span>
        <span class="mock-value" :class="{ 'mock-flag': row.flag }">{{ row.value }}</span>
      </div>
      <div class="mock-divider"></div>
      <div class="mock-note">{{ note }}</div>
      <div class="mock-tag">{{ tag }}</div>
    </div>
  </div>
</template>
