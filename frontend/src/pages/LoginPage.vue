<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useSessionStore } from '../stores/session.store';
import { errorMessage } from '../services/http';

const username = ref('');
const password = ref('');
const busy = ref(false);
const error = ref('');
const showPassword = ref(false);
const session = useSessionStore();
const router = useRouter();
async function submit() {
  busy.value = true;
  error.value = '';
  try {
    await session.signIn(username.value, password.value);
    password.value = '';
    await router.replace(session.home());
  } catch (e) {
    error.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <q-page class="auth-page">
    <section class="auth-story">
      <div class="row items-center q-gutter-sm">
        <div class="brand-mark"><q-icon name="fitness_center" size="28px" /></div>
        <strong>{{ session.config?.name }}</strong>
      </div>
      <h1>Tu espacio.<br />Tu siguiente paso.</h1>
      <p class="text-subtitle1 desktop-copy">
        Una sola cuenta para conectar a clientes, entrenadores y administración.
      </p>
      <div class="text-caption desktop-copy q-mt-xl">Acceso privado · Una sede</div>
    </section>
    <section class="auth-form-area">
      <div class="auth-card">
        <div class="text-overline text-secondary">BIENVENIDO</div>
        <h2 class="text-h4 text-weight-bold q-mt-sm q-mb-md">Inicia sesión</h2>
        <p class="muted q-mb-lg">Ingresa con la cuenta que te proporcionó el gimnasio.</p>
        <q-banner v-if="error" rounded class="bg-red-1 text-negative q-mb-md" role="alert">
          {{ error }}
        </q-banner>
        <q-form class="q-gutter-md" @submit="submit">
          <q-input
            v-model="username"
            outlined
            label="Usuario"
            autocomplete="username"
            :disable="busy"
            :rules="[(v) => !!v || 'Ingresa tu usuario']"
          />
          <q-input
            v-model="password"
            outlined
            label="Contraseña"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            :disable="busy"
            :rules="[(v) => !!v || 'Ingresa tu contraseña']"
          >
            <template #append>
              <q-btn
                flat
                round
                :icon="showPassword ? 'visibility_off' : 'visibility'"
                :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>
          <q-btn
            type="submit"
            color="primary"
            label="Entrar"
            no-caps
            class="full-width"
            :loading="busy"
          />
        </q-form>
        <p class="text-caption muted q-mt-lg">
          Si necesitas recuperar tu acceso, contacta al administrador. La recuperación por correo se
          incorporará en una siguiente entrega.
        </p>
        <q-btn
          v-if="session.config?.registration_enabled"
          flat
          no-caps
          to="/register"
          label="Crear una cuenta de cliente"
        />
      </div>
    </section>
  </q-page>
</template>
