import { defineBoot } from '#q-app/wrappers';
import { useSessionStore } from '../stores/session.store';

export default defineBoot(({ router, store }) => {
  window.addEventListener('api-forbidden', () => {
    const session = useSessionStore(store);
    void session
      .loadUser()
      .then(() => {
        if (!session.user) void router.replace('/login');
      })
      .catch(() => {
        /* The calling screen already shows the network error. */
      });
  });
});
