import { defineRouter } from '#q-app/wrappers';
import { createRouter, createWebHistory } from 'vue-router';
import { useSessionStore } from '../stores/session.store';
import type { Role } from '../types/auth.types';
import { canEnter } from './guards';
import routes from './routes';

export default defineRouter(({ store }) => {
  const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior: () => ({ top: 0 }),
  });
  router.beforeEach(async (to) => {
    if (to.path === '/connection-error') return true;
    const session = useSessionStore(store);
    try {
      await session.init();
    } catch {
      return '/connection-error';
    }
    document.title = session.config?.name || 'Gimnasio';
    const role = to.meta.role as Role | undefined;
    if (role && !session.user) return '/login';
    if (!canEnter(session.user?.roles || [], role)) return '/forbidden';
    if (to.path === '/login' && session.user) return session.home();
    return true;
  });
  return router;
});
