import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api, ApiError, refreshCsrf, setCsrfToken } from '../services/http';
import type { AppConfig, Role, User } from '../types/auth.types';

export const useSessionStore = defineStore('session', () => {
  const user = ref<User | null>(null);
  const config = ref<AppConfig | null>(null);
  const loaded = ref(false);
  let initialization: Promise<void> | null = null;

  async function loadUser() {
    try {
      user.value = await api<User>('/auth/me/');
    } catch (error) {
      if (error instanceof ApiError && error.status === 403) user.value = null;
      else throw error;
    }
  }
  async function init() {
    if (loaded.value) return;
    if (initialization) return initialization;
    initialization = (async () => {
      config.value = await api<AppConfig>('/config/');
      await loadUser();
      loaded.value = true;
    })();
    try {
      await initialization;
    } finally {
      initialization = null;
    }
  }
  async function signIn(username: string, password: string) {
    await refreshCsrf();
    const result = await api<{ user: User; csrfToken: string }>('/auth/login/', {
      method: 'POST',
      body: { username, password },
    });
    user.value = result.user;
    setCsrfToken(result.csrfToken);
  }
  async function signOut() {
    await api<void>('/auth/logout/', { method: 'POST' });
    user.value = null;
    setCsrfToken('');
    // No credentials or client records are persisted in localStorage.
  }
  function hasRole(role: Role) {
    return !!user.value?.roles.includes(role);
  }
  function home() {
    if (hasRole('admin')) return '/admin/dashboard';
    if (hasRole('coach')) return '/coach/dashboard';
    if (hasRole('member')) return '/member/home';
    return '/forbidden';
  }
  return { user, config, loaded, init, loadUser, signIn, signOut, hasRole, home };
});
