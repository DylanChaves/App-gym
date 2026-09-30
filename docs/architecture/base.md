# Arquitectura local

`config/app.json` centraliza nombre, idioma y zona horaria. Al cambiarlo, reinicia Django y reconstruye el frontend para actualizar también el manifiesto. Frontend Quasar CLI + Vue 3 + TypeScript con SCSS. Backend Django REST Framework. Persistencia exclusivamente MySQL 8 con utf8mb4, InnoDB y modo estricto. No hay alternativa SQLite.

En desarrollo el navegador llama `/api` en el puerto 9000 y Quasar lo dirige al puerto 8000. Cookies de sesión HttpOnly, SameSite=Lax; toda escritura autenticada exige CSRF. El login y el autorregistro anónimos también exigen CSRF. No se guardan tokens ni registros de clientes en localStorage.

Las sesiones viven en MySQL. Los roles se almacenan por relación many-to-many; una cuenta puede ser administrador y entrenador. El autorregistro nunca acepta campos administrativos. `createsuperuser` crea también el rol administrador antes de usar el panel. Las banderas técnicas de Django no sustituyen los roles de negocio.

Administración puede listar y gestionar cuentas básicas y asignaciones. Entrenadores consultan su propia cuenta y clientes asignados; clientes, solo su cuenta. Una lectura fuera de alcance devuelve 404; una acción administrativa sin rol devuelve 403. Los listados y detalles usan el mismo selector. Asignaciones requieren cliente y entrenador activos, no admiten autoasignación y se validan dentro de una transacción. Reasignar o retirar la asignación elimina inmediatamente el acceso del entrenador anterior.

Las mutaciones administrativas se serializan con bloqueo de usuarios en orden estable, preservan el último administrador activo y prohíben retirar roles usados por asignaciones. Auditoría almacena responsable, destino, acción, fecha y cambios de roles/identificadores/estado. No almacena contraseñas, cuerpos de peticiones, tokens, correos ni notas. La API de auditoría es de solo lectura para administradores.

Los errores de API son genéricos para fallos internos; respuestas privadas llevan Cache-Control no-store. La consola técnica no permite modificar roles o asignaciones saltándose la API auditada. La limitación de login usa el origen directo y caché en memoria; producción necesita caché compartida y configuración explícita de proxies confiables antes de escalar.

PWA: manifiesto e iconos, shell público precargado, API excluida de caché, actualización explícita sin recarga automática. No se implementa trabajo de entrenamiento offline ni almacenamiento privado local. La recuperación de series se añadirá al módulo de rutinas.
