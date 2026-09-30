import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 120000,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:9000',
    channel: 'msedge',
    headless: true,
    viewport: { width: 1280, height: 900 },
    // Do not record traces containing credentials or request bodies.
    trace: 'off',
    screenshot: 'off',
    video: 'off',
  },
});
