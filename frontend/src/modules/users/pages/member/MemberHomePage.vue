<script setup lang="ts">
import { useSessionStore } from '../../../../stores/session.store';
import EmptyState from '../../../../components/shared/EmptyState.vue';
const session = useSessionStore();
</script>
<template>
  <q-page class="page-content">
    <div class="text-overline text-secondary">TU GIMNASIO</div>
    <h1 class="page-title">Hola, {{ session.user?.first_name || session.user?.username }}</h1>
    <p class="page-subtitle">Tu cuenta está lista. Este será tu espacio de entrenamiento.</p>
    <q-card flat class="surface q-pa-lg q-mb-lg">
      <h2 class="text-h6 q-mt-none">Tu acompañamiento</h2>
      <p>
        {{
          session.user?.coach_id
            ? 'Tienes un entrenador asignado. Contacta al gimnasio para coordinar tu entrenamiento.'
            : 'Todavía no tienes un entrenador asignado. Consulta al administrador cuando tu servicio lo incluya.'
        }}
      </p>
      <q-btn outline color="primary" no-caps label="Consultar mi perfil" to="/member/profile" />
    </q-card>
    <EmptyState
      title="Tu entrenamiento aparecerá aquí"
      description="Las rutinas, reservas, membresías y el progreso todavía no están disponibles en esta primera etapa."
      icon="fitness_center"
    />
  </q-page>
</template>
