const baseUrl = import.meta.env.VITE_API_BASE || '/api';
let csrfToken = '';

export class ApiError extends Error {
  constructor(
    public status: number,
    public details: Record<string, unknown>,
  ) {
    super(
      typeof details.detail === 'string'
        ? details.detail
        : 'Revisa los datos e inténtalo nuevamente.',
    );
  }
}

export function setCsrfToken(token: string) {
  csrfToken = token;
}

export async function refreshCsrf() {
  const response = await fetch(`${baseUrl}/auth/csrf/`, {
    credentials: 'include',
    cache: 'no-store',
  });
  if (!response.ok) throw new Error('No se pudo preparar una conexión segura con el servidor.');
  const data = (await response.json()) as { csrfToken: string };
  csrfToken = data.csrfToken;
}

export async function api<T>(
  path: string,
  options: { method?: string; body?: unknown } = {},
): Promise<T> {
  const method = options.method || 'GET';
  if (method !== 'GET' && !csrfToken) await refreshCsrf();
  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      method,
      credentials: 'include',
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        ...(method !== 'GET' ? { 'X-CSRFToken': csrfToken } : {}),
      },
      ...(options.body !== undefined ? { body: JSON.stringify(options.body) } : {}),
    });
  } catch {
    throw new Error('No hay conexión con la API. Verifica que Django esté iniciado.');
  }
  if (!response.ok) {
    const details = (await response
      .json()
      .catch(() => ({ detail: 'No se pudo completar la solicitud.' }))) as Record<string, unknown>;
    if (response.status === 403 && !path.startsWith('/auth/')) {
      // The store confirms expiration using /me; a role denial alone never logs out.
      window.dispatchEvent(new Event('api-forbidden'));
    }
    throw new ApiError(response.status, details);
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return Object.entries(error.details)
      .map(
        ([key, value]) =>
          `${key === 'detail' || key === 'non_field_errors' ? '' : `${key}: `}${Array.isArray(value) ? value.join(' ') : String(value)}`,
      )
      .join(' ');
  }
  return error instanceof Error ? error.message : 'Ocurrió un error. Inténtalo nuevamente.';
}
