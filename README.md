# Base de la aplicación del gimnasio

Primera etapa para una sede, con cuentas de administrador, entrenador y cliente. Vue 3, Quasar, TypeScript y SCSS; API Django REST Framework; MySQL 8. El administrador también puede tener rol de entrenador. Nombre comercial configurable en `config/app.json`.

El Word original sigue intacto en `../documento/FitGym_Requerimientos_y_Politicas_Costa_Rica_v2.docx`. La estructura sigue su sección 20. No se han realizado push ni despliegues.

## Funciones disponibles

- Inicio/cierre de sesión con cookies HttpOnly y CSRF; consulta del usuario autenticado.
- Administración de cuentas, roles combinables y asignaciones de entrenadores.
- API con listados y detalles filtrados por alcance, protección contra elevar privilegios y preservación del último administrador activo.
- Tres paneles responsivos conectados a la API; edición de cuentas, asignaciones y auditoría desde administración.
- Auditoría de creación, cambios de roles, estados y asignaciones sin contraseñas ni tokens.
- Base de PWA con manifiesto, iconos, exclusión de la API de caché y actualización explícita.
- Registro público implementado y probado, deshabilitado hasta configurar políticas reales y sus versiones. Solo crea clientes.

Membresías, cobros, reservas, asistencia QR/manual, rutinas, progreso y notificaciones aún no están implementados. No se muestran cifras ficticias. Verificación/invitación/recuperación por correo y gestión completa de derechos de privacidad quedan pendientes. No se declara cumplimiento legal certificado.

## Estructura

```text
app/
  config/app.json             nombre, idioma, zona horaria
  frontend/                  Quasar, paneles, módulo users, tests y src-pwa
  backend/                   configuración Django, apps/users, audit, privacy
  docs/                      requisitos, arquitectura, contrato API y pendientes
  infra/local/               MySQL aislado, scripts Windows y alternativa Docker
  infra/cloudflare/          preparación futura del frontend
  infra/backend/             notas del proveedor pendiente
  .github/workflows/         verificaciones sin despliegue
```

## Ejecutar en Windows

Usa **PowerShell 7.2 o superior**, Python 3.12, Node 24 LTS (o 22.22+) y MySQL Server 8.0.43+. No necesitas Docker para la ruta principal. MySQL Shell o Workbench solos no incluyen necesariamente el servidor.

En esta computadora hay MySQL 8.0.43, pero Node del sistema es 22.18 y el lanzador `py` no tiene Python registrado. Los scripts detectan los runtimes compatibles de Codex ya instalados (Python 3.12 y Node 24); no cambian la instalación del sistema.

Abre una terminal en el repositorio existente:

```powershell
cd 'C:\Users\DELL\Desktop\Proyecto gym\app'
git status --short
node --version
py -0p
& 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe' --version
```

### Preparar Python y MySQL aislado

```powershell
.\infra\local\setup-python.ps1
.\infra\local\start-mysql.ps1
.\.venv\Scripts\python.exe backend\manage.py check --database default
.\.venv\Scripts\python.exe backend\manage.py migrate
```

`start-mysql.ps1` crea una instancia exclusiva del proyecto en **127.0.0.1:3307**; no toca el servicio existente en 3306. Usa los binarios instalados y guarda los datos en `.local/mysql-data`. Genera contraseñas aleatorias, protege la cuenta root local y escribe `backend/.env` sin imprimir secretos. `.local/`, `.venv/` y `.env` están ignorados por Git. No sobrescribe un `.env` preexistente al crear la instancia por primera vez.

Si MySQL está en otra ruta:

```powershell
.\infra\local\start-mysql.ps1 -MySqlBin 'D:\MySQL\bin'
```

Los scripts se ejecutan otra vez para arrancar la misma instancia conservando sus datos. Para detenerla de forma ordenada:

```powershell
.\infra\local\stop-mysql.ps1
```

### Alternativa: usar tu servicio MySQL existente

No ejecutes `start-mysql.ps1` para esta opción. Copia el ejemplo y genera una clave local sin imprimirla:

```powershell
Copy-Item backend\.env.example backend\.env
.\.venv\Scripts\python.exe -c "from dotenv import set_key; import secrets; set_key('backend/.env', 'DJANGO_SECRET_KEY', secrets.token_urlsafe(48))"
```

Edita backend/.env para configurar MYSQL_PORT (habitualmente 3306) y las credenciales de una cuenta exclusiva. En MySQL Workbench, conectado como administrador, ejecuta el siguiente SQL sustituyendo la contraseña ficticia antes de ejecutarlo:

```sql
CREATE DATABASE gym_development CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gym_app'@'127.0.0.1' IDENTIFIED BY 'REEMPLAZAR_LOCALMENTE';
GRANT ALL PRIVILEGES ON gym_development.* TO 'gym_app'@'127.0.0.1';
GRANT ALL PRIVILEGES ON gym_test.* TO 'gym_app'@'127.0.0.1';
```

Usa MYSQL_HOST=127.0.0.1. `gym_test` es una base exclusiva de pruebas: Django la crea y elimina, y esa cuenta necesita permisos sobre ella. No apuntes MYSQL_TEST_DATABASE a la base de desarrollo ni a una base existente con datos. Después ejecuta `check --database default` y `migrate` como en la ruta principal.

### Crear tu primer administrador

```powershell
.\.venv\Scripts\python.exe backend\manage.py createsuperuser
```

El comando solicita usuario, correo y contraseña sin mostrarla. El modelo personalizado asigna el rol administrador. Inicia sesión con ese **usuario** (no el correo). La consola técnica `/technical-admin/` es independiente del panel de administración Quasar y no permite saltarse la gestión auditada de roles/asignaciones.

Para una prueba con datos ficticios ya hay cuatro cuentas demo creadas en esta computadora. En otra instalación puedes crearlas con:

```powershell
.\.venv\Scripts\python.exe backend\manage.py seed_demo
```

Sus credenciales están en `.local/demo-credentials.json`, accesible solo como archivo local e ignorado por Git. Cuentas: demo_admin (administrador y entrenador), demo_coach, demo_member (asignado a demo_coach) y demo_other (sin asignación). El comando no cambia contraseñas de cuentas existentes y solo funciona con DEBUG=true. Las pruebas E2E agregan cuentas ficticias con prefijo `e2e_`; pueden desactivarse desde administración.

### Iniciar la API y la interfaz

Terminal 1, desde `app`:

```powershell
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Terminal 2, desde `app`:

```powershell
.\infra\local\frontend.ps1 -Task install
.\infra\local\frontend.ps1 -Task dev
```

Abre **http://127.0.0.1:9000/**. El frontend proxifica `/api` a Django en 8000 para usar el mismo origen. No necesitas editar CORS para esta configuración. `/api/config/` debe responder y `/api/auth/me/` requiere sesión.

En esta computadora ya se instalaron las dependencias y se iniciaron los servidores durante la verificación. Si están detenidos, vuelve a ejecutar start-mysql y los comandos de las dos terminales. Ctrl+C detiene Django o Quasar; MySQL se detiene con su script.

Si dispones de Node compatible en PATH, puedes entrar en frontend y usar directamente `npm ci` y `npm run dev`. El script evita que npm use por accidente el Node 22.18 instalado junto a npm.cmd. `frontend/.env.example` solo contiene configuración pública; `.env` es opcional porque `/api` es el valor predeterminado.

## Comprobar los flujos

1. Como administrador, abre Usuarios y asignaciones, crea una cuenta cliente y otra entrenador, y asigna el cliente. Cambia perfiles y consulta Historial de cambios.
2. Como entrenador, consulta solo tus clientes y abre su perfil. Como cliente, consulta Mi perfil. Una URL de cliente ajeno devuelve 404 en la API.
3. Con demo_admin cambia de Administrador a Entrenador desde el menú de cuenta. Los dos paneles usan la misma identidad.
4. Cierra sesión y comprueba que ya no puedes consultar `/api/auth/me/`.
5. Recarga las cuentas/asignaciones para verificar persistencia MySQL.

## Ejecutar comprobaciones

Desde `app`:

```powershell
.\.venv\Scripts\python.exe -m ruff check backend
.\.venv\Scripts\python.exe -m ruff format --check backend
.\.venv\Scripts\python.exe backend\manage.py check --database default
.\.venv\Scripts\python.exe backend\manage.py makemigrations --check --dry-run
cd backend
..\.venv\Scripts\python.exe manage.py test --settings=config.settings.test --noinput
cd ..
.\infra\local\frontend.ps1 -Task lint
.\infra\local\frontend.ps1 -Task typecheck
.\infra\local\frontend.ps1 -Task test
.\infra\local\frontend.ps1 -Task build
.\infra\local\frontend.ps1 -Task build:pwa
```

Para las pruebas de navegador, primero inicia Django/Quasar y ejecuta seed_demo. Edge debe estar instalado (Playwright usa el canal msedge). Luego:

```powershell
.\infra\local\frontend.ps1 -Task test:e2e
```

Las capturas con datos ficticios se guardan en `.local/screenshots`; no se registran trazas con credenciales. La API conserva su limitación de intentos: si ejecutas muchas pruebas consecutivas, espera el plazo indicado por Retry-After en lugar de desactivar el límite.

La compilación PWA queda en frontend/dist/pwa. Esto comprueba sus recursos y service worker; instalación/actualización en teléfonos reales y despliegue siguen pendientes. No ofrece operación completa sin conexión.

## Documentación y próximos módulos

- `docs/requirements/stage-1.md`: alcance y decisiones pendientes.
- `docs/architecture/base.md`: sesiones, permisos, transacciones y privacidad.
- `docs/api/stage-1.md`: endpoints, campos y códigos de error.
- `docs/policies/pending.md`: condiciones para habilitar autorregistro.
- `docs/verification/stage-1.md`: resultados locales y límites de la verificación.

La configuración de producción y el Dockerfile son preparación; no se ha verificado un entorno Linux, ejecutado CI remoto, certificado cumplimiento ni desplegado la aplicación.
