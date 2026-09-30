<script setup lang="ts">
defineProps<{ title: string; description: string; icon?: string }>();
</script>
<template>
  <q-card flat class="surface q-pa-xl text-center">
    <q-icon :name="icon || 'inbox'" size="40px" color="secondary" class="q-mb-md" />
    <h2 class="text-h6 q-mt-none q-mb-sm">{{ title }}</h2>
    <p class="muted q-mb-none">{{ description }}</p>
    <slot />
  </q-card>
</template>
