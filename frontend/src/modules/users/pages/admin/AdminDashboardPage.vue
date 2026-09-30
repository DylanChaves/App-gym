<script setup lang="ts">
import { useSessionStore } from '../../../../stores/session.store';
import EmptyState from '../../../../components/shared/EmptyState.vue';
const session = useSessionStore();
</script>
<template>
  <q-page class="page-content">
    <div class="text-overline text-secondary">ADMINISTRACIÓN</div>
    <h1 class="page-title">Hola, {{ session.user?.first_name || session.user?.username }}</h1>
    <p class="page-subtitle">
      Gestiona las cuentas del gimnasio y conecta a cada cliente con su entrenador.
    </p>
    <div class="row q-col-gutter-md q-mb-xl">
      <div class="col-12 col-md-6">
        <q-card flat class="surface q-pa-lg">
          <q-icon name="group_add" size="32px" color="primary" />
          <h2 class="text-h6">Usuarios y asignaciones</h2>
          <p class="muted">Crea cuentas, ajusta sus perfiles y asigna entrenadores.</p>
          <q-btn color="primary" to="/admin/users" label="Gestionar usuarios" no-caps />
        </q-card>
      </div>
      <div class="col-12 col-md-6">
        <q-card flat class="surface q-pa-lg">
          <q-icon name="history" size="32px" color="primary" />
          <h2 class="text-h6">Historial de cambios</h2>
          <p class="muted">Consulta quién cambió roles, estados y asignaciones.</p>
          <q-btn outline color="primary" to="/admin/audit" label="Ver historial" no-caps />
        </q-card>
      </div>
    </div>
    <EmptyState
      title="La operación comercial llegará en la siguiente etapa"
      description="Membresías, cobros, caja, reservas y asistencias todavía no están implementados. Aquí aparecerán sus indicadores cuando existan registros reales."
      icon="construction"
    />
  </q-page>
</template>
