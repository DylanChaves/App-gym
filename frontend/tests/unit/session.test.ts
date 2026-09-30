import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useSessionStore } from '../../src/stores/session.store';
import { api, ApiError, setCsrfToken } from '../../src/services/http';
import { canEnter } from '../../src/router/guards';
import type { User } from '../../src/types/auth.types';

const user: User = {
  id: 1,
  username: 'example',
  email: 'example@example.test',
  first_name: '',
  last_name: '',
  is_active: true,
  coach_id: null,
  roles: ['member'],
};
const response = (data: unknown, status = 200) =>
  new Response(status === 204 ? null : JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });

beforeEach(() => {
  setActivePinia(createPinia());
  vi.restoreAllMocks();
  setCsrfToken('');
});

describe('Sesión y navegación', () => {
  it('El login mantiene la sesión en memoria y usa cookies, CSRF y una ruta de cliente', async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(response({ csrfToken: 'csrf-before' }))
      .mockResolvedValueOnce(response({ user, csrfToken: 'csrf-after' }));
    vi.stubGlobal('fetch', fetch);
    const session = useSessionStore();
    await session.signIn('example', 'test-only-password');
    expect(session.user?.id).toBe(1);
    expect(session.home()).toBe('/member/home');
    expect(fetch.mock.calls[1]?.[1]).toMatchObject({
      credentials: 'include',
      headers: { 'X-CSRFToken': 'csrf-before' },
    });
  });
  it('El logout borra la sesión solo después de la confirmación del servidor', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response(null, 204)));
    setCsrfToken('csrf');
    const session = useSessionStore();
    session.user = user;
    await session.signOut();
    expect(session.user).toBeNull();
  });
  it('Un fallo de logout conserva la sesión para reintentar', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    setCsrfToken('csrf');
    const session = useSessionStore();
    session.user = user;
    await expect(session.signOut()).rejects.toThrow('No hay conexión');
    expect(session.user).not.toBeNull();
  });
  it('Una sesión vencida se trata como anónima', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({ detail: 'No autenticado' }, 403)));
    const session = useSessionStore();
    session.user = user;
    await session.loadUser();
    expect(session.user).toBeNull();
  });
  it('Un fallo de red no se confunde con un logout', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    const session = useSessionStore();
    session.user = user;
    await expect(session.loadUser()).rejects.toThrow('No hay conexión');
    expect(session.user?.id).toBe(1);
  });
  it('Los paneles requieren su rol y permiten administrador-entrenador', () => {
    expect(canEnter(['member'], 'admin')).toBe(false);
    expect(canEnter(['coach'], 'member')).toBe(false);
    expect(canEnter(['admin', 'coach'], 'coach')).toBe(true);
    const session = useSessionStore();
    session.user = { ...user, roles: ['admin', 'coach'] };
    expect(session.home()).toBe('/admin/dashboard');
    session.user = { ...user, roles: ['coach'] };
    expect(session.home()).toBe('/coach/dashboard');
  });
  it('El login rechazado no crea una sesión', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValueOnce(response({ csrfToken: 'csrf' }))
        .mockResolvedValueOnce(response({ detail: 'Usuario o contraseña incorrectos.' }, 400)),
    );
    const session = useSessionStore();
    await expect(session.signIn('example', 'wrong')).rejects.toBeInstanceOf(ApiError);
    expect(session.user).toBeNull();
  });
  it('Las respuestas de la API no se almacenan en caché del navegador', async () => {
    const fetch = vi.fn().mockResolvedValue(response(user));
    vi.stubGlobal('fetch', fetch);
    await api('/auth/me/');
    expect(fetch.mock.calls[0]?.[1]).toMatchObject({ cache: 'no-store' });
  });
});
