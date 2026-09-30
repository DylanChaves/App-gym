import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    component: () => import('../layouts/AuthLayout.vue'),
    children: [{ path: '', component: () => import('../pages/LoginPage.vue') }],
  },
  {
    path: '/register',
    component: () => import('../layouts/AuthLayout.vue'),
    children: [{ path: '', component: () => import('../pages/RegisterPage.vue') }],
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { role: 'admin' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      {
        path: 'dashboard',
        component: () => import('../modules/users/pages/admin/AdminDashboardPage.vue'),
      },
      {
        path: 'users',
        component: () => import('../modules/users/pages/admin/UserManagementPage.vue'),
      },
      { path: 'audit', component: () => import('../modules/users/pages/admin/AuditPage.vue') },
    ],
  },
  {
    path: '/coach',
    component: () => import('../layouts/CoachLayout.vue'),
    meta: { role: 'coach' },
    children: [
      { path: '', redirect: '/coach/dashboard' },
      {
        path: 'dashboard',
        component: () => import('../modules/users/pages/coach/CoachDashboardPage.vue'),
      },
    ],
  },
  {
    path: '/member',
    component: () => import('../layouts/MemberLayout.vue'),
    meta: { role: 'member' },
    children: [
      { path: '', redirect: '/member/home' },
      { path: 'home', component: () => import('../modules/users/pages/member/MemberHomePage.vue') },
      {
        path: 'profile',
        component: () => import('../modules/users/pages/member/MemberProfilePage.vue'),
      },
    ],
  },
  { path: '/forbidden', component: () => import('../pages/ForbiddenPage.vue') },
  { path: '/connection-error', component: () => import('../pages/ConnectionErrorPage.vue') },
  { path: '/:catchAll(.*)*', component: () => import('../pages/NotFoundPage.vue') },
];
export default routes;
