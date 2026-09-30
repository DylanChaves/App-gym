<script setup lang="ts">
defineProps<{ message: string }>();
defineEmits<{ retry: [] }>();
</script>
<template>
  <q-banner rounded class="bg-red-1 text-negative q-mb-md" role="alert">
    {{ message }}
    <template #action><q-btn flat label="Reintentar" @click="$emit('retry')" /></template>
  </q-banner>
</template>
