import { test, expect, type Page } from '@playwright/test';
import { readFileSync, mkdirSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import { resolve } from 'node:path';

interface Account {
  username: string;
  password: string;
  id: number;
}
const credentials = JSON.parse(
  readFileSync(resolve('../.local/demo-credentials.json'), 'utf8'),
) as Record<string, Account>;
const output = resolve('../.local/screenshots');
mkdirSync(output, { recursive: true });

async function login(page: Page, name: string) {
  const account = credentials[name];
  if (!account) throw new Error('Ejecuta manage.py seed_demo antes de las pruebas de navegador.');
  await page.goto('/login');
  await page.getByLabel('Usuario', { exact: true }).fill(account.username);
  await page.getByLabel('Contraseña', { exact: true }).fill(account.password);
  for (let attempt = 0; attempt < 2; attempt++) {
    const pending = page.waitForResponse(
      (response) =>
        response.url().endsWith('/api/auth/login/') && response.request().method() === 'POST',
    );
    await page.getByRole('button', { name: 'Entrar', exact: true }).click();
    const response = await pending;
    if (response.status() !== 429) return;
    // Honor the application's actual limit; never disable or bypass it for QA.
    const seconds = Number(response.headers()['retry-after'] || 60);
    if (attempt === 1 || seconds > 60)
      throw new Error('Límite de login activo; espera Retry-After y repite las pruebas.');
    await page.waitForTimeout((seconds + 1) * 1000);
  }
}
async function logout(page: Page) {
  await page.getByRole('button', { name: /^Cuenta de/ }).click();
  await page.getByText('Cerrar sesión', { exact: true }).click();
  await expect(page).toHaveURL(/\/login$/);
  expect((await page.request.get('/api/auth/me/')).status()).toBe(403);
}

test('Los tres perfiles inician sesión en su panel y cierran su sesión real', async ({ page }) => {
  for (const [account, panel] of [
    ['demo_admin', '/admin/dashboard'],
    ['demo_coach', '/coach/dashboard'],
    ['demo_member', '/member/home'],
  ]) {
    await login(page, account!);
    await expect(page).toHaveURL(new RegExp(`${panel}$`));
    expect((await page.request.get('/api/auth/me/')).status()).toBe(200);
    await logout(page);
  }
});

test('Cliente: solo lee sus datos y no entra al panel administrativo', async ({ page }) => {
  await login(page, 'demo_member');
  await expect(page).toHaveURL(/\/member\/home$/);
  const own = credentials.demo_member!;
  const other = credentials.demo_other!;
  expect((await page.request.get(`/api/users/${own.id}/`)).status()).toBe(200);
  expect((await page.request.get(`/api/users/${other.id}/`)).status()).toBe(404);
  const list = await (await page.request.get('/api/users/')).json();
  expect(list.results.map((u: { id: number }) => u.id)).toEqual([own.id]);
  await page.goto('/admin/users');
  await expect(page.getByRole('heading', { name: 'Acceso restringido' })).toBeVisible();
});

test('Entrenador: consulta su cliente y no recibe el cliente ajeno', async ({ page }) => {
  await login(page, 'demo_coach');
  await expect(page).toHaveURL(/\/coach\/dashboard$/);
  await expect(page.getByRole('heading', { name: 'Cliente asignado demo' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Cliente sin asignar demo' })).toHaveCount(0);
  expect((await page.request.get(`/api/users/${credentials.demo_member!.id}/`)).status()).toBe(200);
  expect((await page.request.get(`/api/users/${credentials.demo_other!.id}/`)).status()).toBe(404);
  await page.getByRole('button', { name: 'Ver perfil', exact: true }).first().click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(
    page.getByRole('dialog').getByText('demo_member@example.test', { exact: true }),
  ).toBeVisible();
});

test('Administrador-entrenador cambia de panel sin duplicar cuenta', async ({ page }) => {
  await login(page, 'demo_admin');
  await expect(page).toHaveURL(/\/admin\/dashboard$/);
  await page.getByRole('button', { name: /^Cuenta de/ }).click();
  await page.getByText('Entrenador', { exact: true }).click();
  await expect(page).toHaveURL(/\/coach\/dashboard$/);
  const me = await (await page.request.get('/api/auth/me/')).json();
  expect(me.id).toBe(credentials.demo_admin!.id);
  expect(me.roles).toEqual(expect.arrayContaining(['admin', 'coach']));
});

test('Administrador crea una cuenta desde la interfaz y la asigna; MySQL persiste los cambios', async ({
  page,
}) => {
  await login(page, 'demo_admin');
  await expect(page).toHaveURL(/\/admin\/dashboard$/);
  await page.getByRole('link', { name: 'Gestionar usuarios' }).click();
  await page.getByRole('button', { name: 'Crear usuario' }).click();
  const dialog = page.getByRole('dialog');
  const username = `e2e_${Date.now()}`;
  await dialog.getByLabel('Usuario', { exact: true }).fill(username);
  await dialog.getByLabel('Correo', { exact: true }).fill(`${username}@example.test`);
  await dialog.getByLabel('Nombre', { exact: true }).fill(username);
  await dialog
    .getByLabel('Contraseña inicial', { exact: true })
    .fill(randomBytes(20).toString('hex'));
  await dialog.getByRole('button', { name: 'Guardar', exact: true }).click();
  await expect(dialog).toHaveCount(0);
  const card = page
    .locator('.q-card')
    .filter({ has: page.getByRole('heading', { name: username, exact: true }) });
  await expect(card).toBeVisible();
  await card.getByRole('button', { name: 'Asignar entrenador' }).click();
  await page.getByRole('dialog').getByLabel('Entrenador', { exact: true }).click();
  await page.getByRole('option', { name: 'Entrenador demo', exact: true }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Guardar asignación' }).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await page.reload();
  await expect(card.getByText('Con entrenador asignado')).toBeVisible();
  const result = await (await page.request.get('/api/users/?role=member')).json();
  const saved = result.results.find((u: { username: string }) => u.username === username);
  expect(saved.coach_id).toBe(credentials.demo_coach!.id);
});

test('Login inválido mantiene el formulario y no concede sesión', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Usuario', { exact: true }).fill('absent_account');
  await page.getByLabel('Contraseña', { exact: true }).fill('invalid-test-only');
  await page.getByRole('button', { name: 'Entrar', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('Usuario o contraseña incorrectos.');
  await expect(page).toHaveURL(/\/login$/);
});

test('Vista responsiva: acceso y paneles caben a 360, 768 y 1280 px', async ({ page }) => {
  for (const width of [360, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Inicia sesión' })).toBeVisible();
    await expect
      .poll(() => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))
      .toBe(true);
    await page.screenshot({ path: resolve(output, `login-${width}.png`), fullPage: true });
  }
  for (const [account, panel] of [
    ['demo_admin', '/admin/dashboard'],
    ['demo_coach', '/coach/dashboard'],
    ['demo_member', '/member/home'],
  ]) {
    await login(page, account!);
    await expect(page).toHaveURL(new RegExp(`${panel}$`));
    for (const width of [360, 768, 1280]) {
      await page.setViewportSize({ width, height: 900 });
      await expect
        .poll(() => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))
        .toBe(true);
      await page.screenshot({ path: resolve(output, `${account}-${width}.png`), fullPage: true });
    }
    await logout(page);
  }
});
