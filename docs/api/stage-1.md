# API inicial

Todas las rutas terminan en `/`. JSON; errores 400 de validación, 403 de acceso/CSRF, 404 fuera de alcance y 429 por límite de intentos. Respuestas de error 500 no incluyen detalles internos. Las listas devuelven `{count, next, previous, results}`; 25 registros por página, parámetro `page`, `page_size` máximo 100.

| Método y ruta | Acceso | Resultado |
| --- | --- | --- |
| GET `/api/config/` | Público | Nombre, zona y opciones de registro |
| GET `/api/auth/csrf/` | Público | `csrfToken`, cookie CSRF |
| POST `/api/auth/login/` | Público con CSRF | `{username,password}` → `{user,csrfToken}`; el token rota |
| POST `/api/auth/logout/` | Autenticado con CSRF | 204, sesión invalidada |
| GET `/api/auth/me/` | Autenticado | Cuenta propia |
| POST `/api/auth/register/` | Condicionado, con CSRF | Cuenta cliente; versiones y aceptaciones separadas |
| GET `/api/users/` | Autenticado | Listado filtrado por alcance; `role=admin/coach/member` |
| GET `/api/users/{id}/` | Según alcance | Perfil básico autorizado |
| POST `/api/users/` | Administrador | Cuenta, contraseña inicial y roles |
| PATCH `/api/users/{id}/` | Administrador | Datos básicos, roles y estado |
| POST `/api/users/{id}/coach/` | Administrador | `{coach_id: número o null}` asigna o retira |
| GET `/api/audit/` | Administrador | Historial paginado |

User: id, username, email, first_name, last_name, roles, is_active, coach_id. No expone hashes, permisos técnicos, secretos ni datos privados de salud.

En la creación administrativa se requiere una contraseña válida de al menos diez caracteres. Roles permitidos: admin, coach y member. Los campos is_staff/is_superuser, grupos y permisos técnicos se rechazan. No hay endpoint de eliminación: se desactiva preservando historial. Cambiar contraseña requiere una entrega específica; no se acepta desde PATCH.

Registro: username, email, first_name, last_name, password, terms_version, privacy_version, accept_terms y accept_privacy. Campos adicionales se rechazan. Las dos aceptaciones deben ser afirmativas y coincidir con las versiones actuales; no incluye permisos promocionales ni fotos.

Producción debe servir la API bajo el mismo origen mediante proxy o diseñar y verificar expresamente otra topología de cookies, CSRF y CORS. No basta con cambiar una URL en Cloudflare.
