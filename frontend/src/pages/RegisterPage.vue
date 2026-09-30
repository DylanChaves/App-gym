<script setup lang="ts">
import { reactive, ref } from 'vue';
import { api, errorMessage } from '../services/http';
import { useSessionStore } from '../stores/session.store';
const session = useSessionStore();
const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  accept_terms: false,
  accept_privacy: false,
});
const busy = ref(false);
const error = ref('');
const success = ref(false);
async function submit() {
  busy.value = true;
  error.value = '';
  try {
    await api('/auth/register/', {
      method: 'POST',
      body: {
        ...form,
        terms_version: session.config?.terms_version,
        privacy_version: session.config?.privacy_version,
      },
    });
    form.password = '';
    success.value = true;
  } catch (e) {
    error.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <q-page class="page-content" style="max-width: 560px">
    <h1 class="page-title">Crear cuenta</h1>
    <q-banner v-if="!session.config?.registration_enabled" class="bg-orange-1">
      El autorregistro aún no está habilitado. Solicita tu cuenta al administrador.
    </q-banner>
    <q-banner v-else-if="success" class="bg-green-1">
      Tu cuenta de cliente está creada. Ya puedes iniciar sesión.
    </q-banner>
    <q-form v-else class="q-gutter-md" @submit="submit">
      <q-banner v-if="error" class="bg-red-1 text-negative" role="alert">{{ error }}</q-banner>
      <q-input
        v-model="form.username"
        outlined
        label="Usuario"
        autocomplete="username"
        :rules="[(v) => !!v || 'Campo obligatorio']"
      />
      <q-input
        v-model="form.email"
        outlined
        label="Correo"
        type="email"
        autocomplete="email"
        :rules="[(v) => !!v || 'Campo obligatorio']"
      />
      <q-input v-model="form.first_name" outlined label="Nombre" autocomplete="given-name" />
      <q-input v-model="form.last_name" outlined label="Apellidos" autocomplete="family-name" />
      <q-input
        v-model="form.password"
        outlined
        label="Contraseña"
        type="password"
        autocomplete="new-password"
        hint="Al menos 10 caracteres; evita datos personales y contraseñas comunes."
        :rules="[(v) => v.length >= 10 || 'Usa al menos 10 caracteres']"
      />
      <p>
        <a :href="session.config?.terms_url" target="_blank" rel="noopener">Leer contrato</a> ·
        <a :href="session.config?.privacy_url" target="_blank" rel="noopener"
          >Leer aviso de privacidad</a
        >
      </p>
      <q-checkbox v-model="form.accept_terms" label="Acepto el contrato de servicio" />
      <q-checkbox
        v-model="form.accept_privacy"
        label="Consiento el tratamiento operativo descrito en el aviso"
      />
      <q-btn
        type="submit"
        label="Crear cuenta de cliente"
        color="primary"
        no-caps
        :loading="busy"
        :disable="!form.accept_terms || !form.accept_privacy"
      />
    </q-form>
    <q-btn flat to="/login" label="Volver al acceso" no-caps class="q-mt-lg" />
  </q-page>
</template>
