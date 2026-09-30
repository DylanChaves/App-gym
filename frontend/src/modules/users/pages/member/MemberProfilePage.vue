<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api, errorMessage } from '../../../../services/http';
import type { User } from '../../../../types/auth.types';
import ErrorState from '../../../../components/shared/ErrorState.vue';
import LoadingState from '../../../../components/shared/LoadingState.vue';
const user = ref<User | null>(null);
const busy = ref(false);
const error = ref('');
async function load() {
  busy.value = true;
  error.value = '';
  try {
    user.value = await api<User>('/auth/me/');
  } catch (e) {
    user.value = null;
    error.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
onMounted(load);
</script>
<template>
  <q-page class="page-content">
    <h1 class="page-title">Mi perfil</h1>
    <p class="page-subtitle">Datos de tu cuenta. Para corregirlos, contacta al administrador.</p>
    <ErrorState v-if="error" :message="error" @retry="load" /><LoadingState v-if="busy" /><q-card
      v-else-if="user"
      flat
      class="surface q-pa-lg"
      style="max-width: 620px"
    >
      <dl style="overflow-wrap: anywhere">
        <dt class="muted">Nombre</dt>
        <dd class="q-ml-none q-mb-lg">
          {{ `${user.first_name} ${user.last_name}`.trim() || 'Sin nombre registrado' }}
        </dd>
        <dt class="muted">Usuario</dt>
        <dd class="q-ml-none q-mb-lg">{{ user.username }}</dd>
        <dt class="muted">Correo</dt>
        <dd class="q-ml-none q-mb-lg">{{ user.email }}</dd>
        <dt class="muted">Entrenamiento</dt>
        <dd class="q-ml-none">
          {{ user.coach_id ? 'Con entrenador asignado' : 'Sin entrenador asignado' }}
        </dd>
      </dl>
    </q-card>
  </q-page>
</template>
