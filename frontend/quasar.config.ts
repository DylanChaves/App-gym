import { defineConfig } from '#q-app/wrappers';
import { readFileSync } from 'node:fs';

const app = JSON.parse(readFileSync(new URL('../config/app.json', import.meta.url), 'utf8')) as {
  name: string;
};

export default defineConfig(() => ({
  boot: ['api'],
  css: ['app.scss'],
  extras: ['material-icons'],
  build: {
    vueRouterMode: 'history',
    target: { browser: ['es2022'], node: 'node22' },
  },
  devServer: {
    host: '127.0.0.1',
    port: 9000,
    open: false,
    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: false } },
  },
  framework: { lang: 'es', plugins: ['Notify', 'Dialog'] },
  pwa: {
    workboxMode: 'GenerateSW',
    injectPwaMetaTags: ({ publicPath }) =>
      `<meta name="mobile-web-app-capable" content="yes"><link rel="apple-touch-icon" href="${publicPath}icons/icon-192.png">`,
    swFilename: 'sw.js',
    manifestFilename: 'manifest.json',
    useCredentialsForManifestTag: false,
    extendGenerateSWOptions(options) {
      // Only the public application shell is cached. Never cache authenticated API data.
      options.skipWaiting = false;
      options.clientsClaim = false;
      options.navigateFallbackDenylist = [/^\/api\//, /^\/technical-admin\//];
      options.runtimeCaching = [];
    },
    extendManifestJson(manifest) {
      manifest.name = app.name;
      manifest.short_name = app.name;
    },
  },
}));
