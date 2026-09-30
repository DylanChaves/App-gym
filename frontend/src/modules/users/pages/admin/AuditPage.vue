<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api, errorMessage } from '../../../../services/http';
import type { Page } from '../../../../types/api.types';
import EmptyState from '../../../../components/shared/EmptyState.vue';
import ErrorState from '../../../../components/shared/ErrorState.vue';
import LoadingState from '../../../../components/shared/LoadingState.vue';
interface Audit {
  id: number;
  actor_id: number | null;
  target_id: number;
  action: string;
  changes: Record<string, unknown>;
  created_at: string;
}
const items = ref<Audit[]>([]);
const page = ref(1);
const maxPage = ref(1);
const busy = ref(false);
const error = ref('');
const labels: Record<string, string> = {
  'user.created': 'Cuenta creada',
  'roles.changed': 'Perfiles cambiados',
  'user.status_changed': 'Estado de cuenta cambiado',
  'assignment.changed': 'Asignación cambiada',
};
async function load() {
  busy.value = true;
  error.value = '';
  try {
    const result = await api<Page<Audit>>(`/audit/?page=${page.value}`);
    items.value = result.results;
    maxPage.value = Math.max(1, Math.ceil(result.count / 25));
  } catch (e) {
    items.value = [];
    error.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-CR', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'America/Costa_Rica',
  }).format(new Date(value));
}
onMounted(load);
</script>
<template>
  <q-page class="page-content">
    <h1 class="page-title">Historial de cambios</h1>
    <p class="page-subtitle">Roles, estados y asignaciones. Horarios de Costa Rica.</p>
    <ErrorState v-if="error" :message="error" @retry="load" /><LoadingState v-if="busy" />
    <EmptyState
      v-else-if="!error && !items.length"
      title="Sin cambios registrados"
      description="Los cambios realizados desde la gestión de usuarios aparecerán aquí."
    />
    <div v-else class="q-gutter-md">
      <q-card v-for="item in items" :key="item.id" flat class="surface q-pa-lg">
        <strong>{{ labels[item.action] || item.action }}</strong>
        <div class="text-caption muted q-mt-sm">
          {{ formatDate(item.created_at) }} · Cuenta {{ item.target_id }} · Responsable
          {{ item.actor_id || 'Autorregistro' }}
        </div>
        <div class="q-mt-sm" style="overflow-wrap: anywhere">
          {{ JSON.stringify(item.changes) }}
        </div>
      </q-card>
    </div>
    <q-pagination
      v-if="maxPage > 1"
      v-model="page"
      :max="maxPage"
      class="q-mt-lg"
      @update:model-value="load"
    />
  </q-page>
</template>
