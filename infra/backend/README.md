# Backend futuro

Proveedor pendiente. El Dockerfile se construye desde la raíz del repositorio (`docker build -f backend/Dockerfile .`). No se ha ejecutado un despliegue. Secretos fuera de la imagen; configuración config.settings.production. Antes de producción: TLS y proxy confiable, caché compartida para límites de login, MFA del personal, correo, backups/restauración, límites operativos, monitorización y políticas aprobadas. Aplicar migraciones mediante un proceso controlado, no automáticamente en cada inicio de worker.
