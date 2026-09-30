# Primera etapa

Fuente: `../../../documento/FitGym_Requerimientos_y_Politicas_Costa_Rica_v2.docx`, versión 2.1 y anexo de la sección 20. El original permanece fuera del repositorio, sin modificaciones.

Implementación: una sede; tres roles combinables; usuarios administrados, asignaciones, acceso por sesión, paneles responsivos, auditoría y PWA básica. El nombre se cambia en `config/app.json` y requiere reconstruir el frontend para actualizar el manifiesto.

No hay modelos ni indicadores ficticios para pagos, membresías, asistencias, reservas, rutinas o progreso. El administrador reúne la operación de recepción cuando se implementen esos módulos. Un rol administrativo no otorgará automáticamente acceso a futuras fotos o notas sensibles. Esos permisos deberán añadirse en cada módulo con pruebas propias.

La organización sigue frontend, backend, docs, infra y módulos de la sección 20. Solo se crean aplicaciones y componentes cuando tienen uso: `users`, `audit` y `privacy` están implementados; las aplicaciones de etapas posteriores no son carpetas vacías presentadas como funcionalidades.

## Decisiones pendientes

- Planes: duración, servicios y horarios; renovaciones y congelamientos.
- Pagos: descuentos, devoluciones, caja, pasarela y mecanismo fiscal.
- Agenda: plazos y consecuencias de faltas, reserva y cancelación.
- Rutinas: secuencia flexible o fechas fijas; biblioteca autorizada.
- Marca: nombre, logo y paleta definitiva. La paleta actual es provisional.
- Producción: proveedor Django/MySQL, regiones, correo, almacenamiento privado, tareas y monitoreo.
- Privacidad: operador y contactos, políticas aprobadas, conservación, gestión de derechos, menores y clasificación de datos sensibles.

El autorregistro está implementado y probado, pero deshabilitado por defecto. Se habilita únicamente al configurar documentos y versiones reales. No se publican las políticas incompletas del Word. En esta entrega el gimnasio puede crear cuentas desde el panel administrativo. Verificación de correo, invitaciones y recuperación por correo quedan para una entrega siguiente; no se muestran como funcionales.

Los consentimientos iniciales conservan versión, finalidad y fecha. Revocación, purgas, exportación de derechos e incidentes todavía requieren implementación. Esta base no acredita cumplimiento legal certificado.

Fuera de esta primera versión: IA, huella digital, biometría, multisedes, torniquetes, operación completa sin conexión, WhatsApp y cobros recurrentes. El QR y el registro manual de asistencia pertenecen a una etapa posterior.
