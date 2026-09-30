<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useSessionStore } from '../../stores/session.store';
import { errorMessage } from '../../services/http';
import { roleLabels, type Role } from '../../types/auth.types';

const props = defineProps<{ role: Role; links: { label: string; icon: string; to: string }[] }>();
const session = useSessionStore();
const router = useRouter();
const drawer = ref(false);
const leaving = ref(false);
const error = ref('');
const pendingUpdate = ref<ServiceWorkerRegistration | null>(null);
const roles = computed(
  () => session.user?.roles.map((role) => ({ label: roleLabels[role], value: role })) || [],
);
const userName = computed(() => session.user?.first_name || session.user?.username);

function switchPanel(role: Role) {
  void router.push(role === 'member' ? '/member/home' : `/${role}/dashboard`);
}
async function logout() {
  leaving.value = true;
  error.value = '';
  try {
    await session.signOut();
    await router.replace('/login');
  } catch (e) {
    error.value = errorMessage(e);
  } finally {
    leaving.value = false;
  }
}
function updateAvailable(event: Event) {
  pendingUpdate.value = (event as CustomEvent<ServiceWorkerRegistration>).detail;
}
function applyUpdate() {
  if (!pendingUpdate.value?.waiting) return;
  navigator.serviceWorker.addEventListener('controllerchange', () => window.location.reload(), {
    once: true,
  });
  pendingUpdate.value.waiting.postMessage({ type: 'SKIP_WAITING' });
}
onMounted(() => window.addEventListener('pwa-update', updateAvailable));
onUnmounted(() => window.removeEventListener('pwa-update', updateAvailable));
</script>
<template>
  <q-layout view="hHh Lpr fFf">
    <q-header class="bg-white text-dark" bordered>
      <q-toolbar class="q-px-md" style="min-height: 72px">
        <q-btn
          v-if="props.role !== 'member'"
          flat
          round
          icon="menu"
          aria-label="Abrir navegación"
          @click="drawer = !drawer"
        />
        <div class="brand-mark q-mr-sm"><q-icon name="fitness_center" size="24px" /></div>
        <q-toolbar-title class="text-weight-bold">{{ session.config?.name }}</q-toolbar-title>
        <q-btn flat round icon="account_circle" :aria-label="`Cuenta de ${userName}`">
          <q-menu>
            <q-list style="min-width: 230px">
              <q-item>
                <q-item-section>
                  <q-item-label>{{ userName }}</q-item-label
                  ><q-item-label caption>{{ roleLabels[props.role] }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item
                v-for="option in roles"
                :key="option.value"
                clickable
                @click="switchPanel(option.value)"
              >
                <q-item-section>{{ option.label }}</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable :disable="leaving" @click="logout">
                <q-item-section avatar><q-icon name="logout" /></q-item-section
                ><q-item-section>Cerrar sesión</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>
    <q-drawer
      v-if="props.role !== 'member'"
      v-model="drawer"
      show-if-above
      bordered
      :width="250"
      :breakpoint="900"
      class="bg-white"
    >
      <div class="q-pa-lg text-overline">{{ roleLabels[props.role] }}</div>
      <q-list padding>
        <q-item
          v-for="link in links"
          :key="link.to"
          clickable
          :to="link.to"
          active-class="bg-green-1 text-primary"
          @click="drawer = false"
        >
          <q-item-section avatar><q-icon :name="link.icon" /></q-item-section
          ><q-item-section>{{ link.label }}</q-item-section>
        </q-item>
      </q-list>
      <div class="q-pa-lg muted text-caption">Una sede · Atención y entrenamiento</div>
    </q-drawer>
    <q-page-container>
      <q-banner v-if="error" class="bg-red-1 text-negative" role="alert">{{ error }}</q-banner>
      <q-banner v-if="pendingUpdate" class="bg-blue-1">
        Hay una actualización disponible. Aplícala cuando hayas terminado tus cambios.
        <template #action><q-btn flat label="Actualizar ahora" @click="applyUpdate" /></template>
      </q-banner>
      <router-view />
    </q-page-container>
    <q-footer v-if="props.role === 'member'" bordered class="bg-white text-primary">
      <q-tabs no-caps>
        <q-route-tab
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          :icon="link.icon"
          :label="link.label"
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>
