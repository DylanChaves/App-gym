<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useSessionStore } from '../../../../stores/session.store';
import {
  assignCoach,
  createUser,
  getCoaches,
  getUsers,
  updateUser,
  type UserInput,
} from '../../services/users.api';
import { roleLabels, type Role, type User } from '../../../../types/auth.types';
import { errorMessage } from '../../../../services/http';
import ErrorState from '../../../../components/shared/ErrorState.vue';
import LoadingState from '../../../../components/shared/LoadingState.vue';
import EmptyState from '../../../../components/shared/EmptyState.vue';

const q = useQuasar();
const users = ref<User[]>([]);
const coaches = ref<User[]>([]);
const session = useSessionStore();
const router = useRouter();
const page = ref(1);
const count = ref(0);
const busy = ref(false);
const error = ref('');
const editor = ref(false);
const editing = ref<User | null>(null);
const saving = ref(false);
const formError = ref('');
const assignment = ref<User | null>(null);
const coachId = ref<number | null>(null);
const assignmentOpen = ref(false);
const form = reactive<UserInput>({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  roles: ['member'],
  is_active: true,
  password: '',
});
const roleOptions = (Object.keys(roleLabels) as Role[]).map((role) => ({
  label: roleLabels[role],
  value: role,
}));
const coachOptions = computed(() => [
  { label: 'Sin entrenador', value: null },
  ...coaches.value
    .filter((c) => c.id !== assignment.value?.id)
    .map((c) => ({ label: `${c.first_name} ${c.last_name}`.trim() || c.username, value: c.id })),
]);
const maxPage = computed(() => Math.max(1, Math.ceil(count.value / 25)));

async function load() {
  busy.value = true;
  error.value = '';
  try {
    const result = await getUsers(page.value);
    users.value = result.results;
    count.value = result.count;
  } catch (e) {
    users.value = [];
    error.value = errorMessage(e);
  } finally {
    busy.value = false;
  }
}
function openEditor(user: User | null) {
  editing.value = user;
  formError.value = '';
  Object.assign(form, {
    username: user?.username || '',
    email: user?.email || '',
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    roles: user ? [...user.roles] : ['member'],
    is_active: user?.is_active ?? true,
    password: '',
  });
  editor.value = true;
}
async function save() {
  const perform = async () => {
    saving.value = true;
    formError.value = '';
    try {
      const { password, ...data } = form;
      if (editing.value) await updateUser(editing.value.id, data);
      else await createUser({ ...data, password });
      form.password = '';
      editor.value = false;
      q.notify({ type: 'positive', message: 'Cuenta guardada.' });
      if (editing.value?.id === session.user?.id) {
        await session.loadUser();
        if (!session.hasRole('admin')) {
          await router.replace(session.user ? session.home() : '/login');
          return;
        }
      }
      await load();
    } catch (e) {
      formError.value = errorMessage(e);
    } finally {
      saving.value = false;
    }
  };
  if (editing.value && !form.is_active) {
    q.dialog({
      title: 'Desactivar cuenta',
      message: 'La persona perderá el acceso. Sus registros y el historial se conservarán.',
      cancel: true,
      persistent: true,
    }).onOk(() => {
      void perform();
    });
  } else await perform();
}
async function openAssignment(user: User) {
  assignment.value = user;
  coachId.value = user.coach_id;
  formError.value = '';
  saving.value = true;
  assignmentOpen.value = true;
  try {
    coaches.value = await getCoaches();
  } catch (e) {
    coaches.value = [];
    formError.value = errorMessage(e);
  } finally {
    saving.value = false;
  }
}
async function saveAssignment() {
  if (!assignment.value) return;
  saving.value = true;
  formError.value = '';
  try {
    await assignCoach(assignment.value.id, coachId.value);
    assignmentOpen.value = false;
    q.notify({ type: 'positive', message: 'Asignación guardada.' });
    await load();
  } catch (e) {
    formError.value = errorMessage(e);
  } finally {
    saving.value = false;
  }
}
onMounted(load);
</script>
<template>
  <q-page class="page-content">
    <div class="row items-start justify-between q-gutter-md q-mb-lg">
      <div>
        <h1 class="page-title">Usuarios y asignaciones</h1>
        <p class="muted q-mb-none">Los perfiles pueden combinarse en una misma cuenta.</p>
      </div>
      <q-btn
        color="primary"
        icon="person_add"
        label="Crear usuario"
        no-caps
        @click="openEditor(null)"
      />
    </div>
    <ErrorState v-if="error" :message="error" @retry="load" />
    <LoadingState v-if="busy" />
    <EmptyState
      v-else-if="!error && !users.length"
      title="Aún no hay usuarios"
      description="Crea la primera cuenta de cliente o entrenador."
    />
    <div v-else class="user-grid">
      <q-card v-for="user in users" :key="user.id" flat class="surface q-pa-lg">
        <div class="row items-center justify-between">
          <q-avatar color="green-1" text-color="primary" icon="person" /><q-badge
            :color="user.is_active ? 'positive' : 'grey-7'"
          >
            {{ user.is_active ? 'Activa' : 'Inactiva' }}
          </q-badge>
        </div>
        <h2 class="text-h6 q-mb-xs">
          {{ `${user.first_name} ${user.last_name}`.trim() || user.username }}
        </h2>
        <div class="muted" style="overflow-wrap: anywhere">
          {{ user.username }} · {{ user.email }}
        </div>
        <div class="q-mt-md q-gutter-xs">
          <q-chip v-for="role in user.roles" :key="role" dense color="green-1" text-color="primary">
            {{ roleLabels[role] }}
          </q-chip>
        </div>
        <p v-if="user.roles.includes('member')" class="text-caption muted q-mt-md">
          {{ user.coach_id ? 'Con entrenador asignado' : 'Sin entrenador asignado' }}
        </p>
        <div class="row q-gutter-sm q-mt-md">
          <q-btn
            outline
            color="primary"
            label="Editar cuenta"
            no-caps
            @click="openEditor(user)"
          /><q-btn
            v-if="user.roles.includes('member')"
            flat
            color="primary"
            label="Asignar entrenador"
            no-caps
            :disable="!user.is_active"
            @click="openAssignment(user)"
          />
        </div>
      </q-card>
    </div>
    <q-pagination
      v-if="maxPage > 1"
      v-model="page"
      :max="maxPage"
      :max-pages="5"
      boundary-numbers
      class="q-mt-lg"
      @update:model-value="load"
    />
    <q-dialog v-model="editor" persistent>
      <q-card class="q-pa-lg" style="width: 540px; max-width: 95vw">
        <h2 class="text-h6 q-mt-none">{{ editing ? 'Editar cuenta' : 'Crear usuario' }}</h2>
        <q-banner v-if="formError" class="bg-red-1 text-negative q-mb-md" role="alert">
          {{ formError }}
        </q-banner>
        <q-form class="q-gutter-md" @submit="save">
          <q-input
            v-model="form.username"
            outlined
            label="Usuario"
            :disable="saving"
            :rules="[(v) => !!v || 'Campo obligatorio']"
          />
          <q-input
            v-model="form.email"
            outlined
            label="Correo"
            type="email"
            :disable="saving"
            :rules="[(v) => !!v || 'Campo obligatorio']"
          />
          <q-input v-model="form.first_name" outlined label="Nombre" :disable="saving" />
          <q-input v-model="form.last_name" outlined label="Apellidos" :disable="saving" />
          <q-select
            v-model="form.roles"
            :options="roleOptions"
            outlined
            label="Perfiles"
            multiple
            emit-value
            map-options
            use-chips
            :disable="saving"
            :rules="[(v) => v.length > 0 || 'Selecciona al menos un perfil']"
          />
          <q-input
            v-if="!editing"
            v-model="form.password"
            outlined
            type="password"
            label="Contraseña inicial"
            autocomplete="new-password"
            :disable="saving"
            hint="Entrégala por un canal privado. Usa al menos 10 caracteres."
            :rules="[(v) => v.length >= 10 || 'Usa al menos 10 caracteres']"
          />
          <q-toggle v-model="form.is_active" label="Cuenta activa" :disable="saving" />
          <div class="row justify-end q-gutter-sm">
            <q-btn
              flat
              label="Cancelar"
              no-caps
              :disable="saving"
              @click="
                editor = false;
                form.password = '';
              "
            /><q-btn type="submit" label="Guardar" color="primary" no-caps :loading="saving" />
          </div>
        </q-form>
      </q-card>
    </q-dialog>
    <q-dialog v-model="assignmentOpen" persistent>
      <q-card class="q-pa-lg" style="width: 460px; max-width: 95vw">
        <h2 class="text-h6 q-mt-none">Asignar entrenador</h2>
        <p>{{ assignment?.first_name || assignment?.username }}</p>
        <q-banner v-if="formError" class="bg-red-1 text-negative q-mb-md" role="alert">
          {{ formError }}
        </q-banner>
        <q-select
          v-model="coachId"
          outlined
          label="Entrenador"
          :options="coachOptions"
          emit-value
          map-options
          :disable="saving"
        />
        <div class="row justify-end q-gutter-sm q-mt-lg">
          <q-btn
            flat
            label="Cancelar"
            no-caps
            :disable="saving"
            @click="assignmentOpen = false"
          /><q-btn
            color="primary"
            label="Guardar asignación"
            no-caps
            :loading="saving"
            @click="saveAssignment"
          />
        </div>
      </q-card>
    </q-dialog>
  </q-page>
</template>
