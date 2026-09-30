# Frontend futuro en Cloudflare

Preparación local: `npm ci` y `npm run build:pwa` desde frontend con Node compatible. Directorio final: frontend/dist/pwa. El nombre del manifiesto proviene de config/app.json. No se ha publicado ni contratado ningún servicio.

El modo history exige fallback de rutas a index.html. Antes de publicar, seleccionar dominio y configurar un proxy seguro de `/api` al backend, cookies, HTTPS y orígenes CSRF. Nunca exponer secretos mediante variables VITE. MySQL y Django requieren un proveedor independiente por seleccionar. No se añade workflow de despliegue en esta entrega.
