<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getUser, getUsers } from '../../services/users.api';
import type { User } from '../../../../types/auth.types';
import { errorMessage } from '../../../../services/http';
import EmptyState from '../../../../components/shared/EmptyState.vue';
import ErrorState from '../../../../components/shared/ErrorState.vue';
import LoadingState from '../../../../components/shared/LoadingState.vue';
const users = ref<User[]>([]);
const detail = ref<User | null>(null);
const showDetail = ref(false);
const page = ref(1);
const maxPage = ref(1);
const busy = ref(false);
const error = ref('');
async function load() {
  busy.value = true;
  error.value = '';
  try {
    const result = await getUsers(page.value, 'member', true);
    users.value = result.results;
    maxPage.value = Math.max(1, Math.ceil(result.count / 25));
  } catch (e) {
    users.value = [];
    error.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
async function view(user: User) {
  try {
    detail.value = await getUser(user.id);
    showDetail.value = true;
  } catch (e) {
    error.value = errorMessage(e);
  }
}
onMounted(load);
</script>
<template>
  <q-page class="page-content">
    <div class="text-overline text-secondary">ENTRENAMIENTO</div>
    <h1 class="page-title">Mis clientes</h1>
    <p class="page-subtitle">Consulta las cuentas de los clientes que tienes asignados.</p>
    <ErrorState v-if="error" :message="error" @retry="load" /><LoadingState v-if="busy" />
    <EmptyState
      v-else-if="!error && !users.length"
      title="Todavía no tienes clientes asignados"
      description="El administrador podrá asignarte clientes desde su panel."
      icon="people_outline"
    />
    <div v-else class="user-grid">
      <q-card v-for="user in users" :key="user.id" flat class="surface q-pa-lg">
        <q-avatar icon="person" color="green-1" text-color="primary" />
        <h2 class="text-h6">
          {{ `${user.first_name} ${user.last_name}`.trim() || user.username }}
        </h2>
        <p class="muted" style="overflow-wrap: anywhere">{{ user.email }}</p>
        <q-btn outline no-caps color="primary" label="Ver perfil" @click="view(user)" />
      </q-card>
    </div>
    <q-pagination
      v-if="maxPage > 1"
      v-model="page"
      :max="maxPage"
      class="q-mt-lg"
      @update:model-value="load"
    />
    <div class="q-mt-xl">
      <EmptyState
        title="Rutinas y seguimiento pendientes"
        description="La biblioteca, la creación de rutinas y el seguimiento se implementarán en sus etapas correspondientes."
        icon="construction"
      />
    </div>
    <q-dialog v-model="showDetail">
      <q-card v-if="detail" class="q-pa-lg" style="width: 420px; max-width: 95vw">
        <h2 class="text-h6">{{ detail.first_name || detail.username }} {{ detail.last_name }}</h2>
        <p style="overflow-wrap: anywhere">{{ detail.email }}</p>
        <p>Cuenta {{ detail.is_active ? 'activa' : 'inactiva' }}</p>
        <q-btn v-close-popup flat color="primary" label="Cerrar" no-caps />
      </q-card>
    </q-dialog>
  </q-page>
</template>
