# Verificación de la primera etapa

Realizada localmente el 30 de septiembre de 2026. Repositorio existente, sin push ni despliegue. El Word original permanece fuera de app; SHA256 de referencia: `02A99701E331473B8FFEDF58B2D70DC4BCE05F2305031ADE8A3EB13AD25258F0`.

## Verificado correctamente

| Comprobación | Resultado |
| --- | --- |
| MySQL | Instancia exclusiva 8.0.43, 127.0.0.1:3307; migraciones aplicadas; cuentas y asignaciones conservadas tras detener y reiniciar el servidor |
| Django check con base de datos | Sin problemas |
| Consistencia de migraciones | Sin cambios pendientes |
| Pruebas Django sobre MySQL | 21 aprobadas; no se utilizó SQLite |
| Ruff y formato Python | Aprobados |
| ESLint | Aprobado sin errores ni advertencias |
| TypeScript | Aprobado |
| Vitest | 8 pruebas aprobadas |
| Compilación SPA | Aprobada |
| Compilación PWA y service worker | Aprobada; manifiesto e iconos presentes |
| Edge con Playwright | 7 recorridos aprobados |
| Diseño responsivo | Login y tres paneles a 360, 768 y 1280 px, sin desbordamiento horizontal al estabilizar la distribución |
| Revisión visual | Capturas de móvil y escritorio inspeccionadas con datos ficticios |
| Secretos locales | .env, .local, .venv, dependencias y resultados ignorados por Git; no se añaden contraseñas reales al código |
| Dependencias frontend | npm audit: 0 vulnerabilidades después de actualizar Vitest y esbuild |

Las pruebas cubren login/logout real, sesiones inválidas, CSRF, bloqueo de cuentas inactivas, listados/detalles filtrados, cliente ajeno, entrenador no asignado, prohibición de mutaciones administrativas para otros roles, administrador-entrenador, cambios de asignación, auditoría, último administrador, campos técnicos rechazados, registro público condicionado, aceptaciones versionadas, respuestas no cacheables y limitación de login.

Los recorridos Edge incluyen creación de cliente y asignación mediante la interfaz, recarga y consulta API que confirma persistencia. La prueba respeta Retry-After cuando llega al límite de intentos; no se desactiva el control para pasar QA.

Se corrigieron la compatibilidad de Node usando el runtime 24.19, un fallo interno de npm 10 al modificar dependencias usando npm 11 temporalmente, el manifiesto PWA requerido por Quasar y selectores/tiempos de estabilización de las pruebas de interfaz. También se corrigió una carrera entre cierre y arranque de MySQL esperando la retirada del PID antes de reiniciar. npm ci se comprobó mediante dry-run sin modificar las dependencias activas. Los fallos iniciales no se consideran comprobaciones aprobadas; la tabla refleja los resultados posteriores.

## Implementado pero no verificado en su entorno final

- Configuración de producción, Dockerfile y alternativa Compose: sin ejecución Docker/Linux.
- Workflow de verificaciones: no ejecutado en GitHub porque no se hizo push.
- Instalación y actualización PWA en teléfonos reales: pendiente de Android/iPhone y dominio final.
- Registro público habilitado con políticas reales: no activado; la API se prueba con versiones ficticias solo en la base de tests.

## Pendiente

Módulos comerciales, agenda/asistencia QR/manual, rutinas/progreso/notificaciones/reportes; correo e invitaciones/recuperación/verificación; políticas aprobadas, derechos, conservación y tratamiento sensible; infraestructura de producción, MFA, cache compartida para límites, backups/restauración y monitoreo. Detalles en docs/requirements/stage-1.md.

No hay un bloqueo externo para usar la base local con MySQL. Los componentes de producción y etapas posteriores no se presentan como operativos ni como cumplimiento legal certificado.
