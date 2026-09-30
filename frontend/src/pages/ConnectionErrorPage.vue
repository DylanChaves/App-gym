<script setup lang="ts">
function retry() {
  window.location.assign('/login');
}
</script>
<template>
  <q-layout>
    <q-page-container>
      <q-page class="page-content">
        <h1 class="page-title">No pudimos conectar</h1>
        <p>Verifica que la API Django y MySQL estén iniciados.</p>
        <q-btn color="primary" label="Reintentar conexión" no-caps @click="retry" />
      </q-page>
    </q-page-container>
  </q-layout>
</template>
