import { register } from 'register-service-worker';

// Wait for explicit user confirmation before applying updates. Never auto-reload a session.
register(process.env.SERVICE_WORKER_FILE!, {
  updated(registration) {
    window.dispatchEvent(new CustomEvent('pwa-update', { detail: registration }));
  },
});
