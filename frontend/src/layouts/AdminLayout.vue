<script setup lang="ts">
import PanelShell from '../components/navigation/PanelShell.vue';
const links = [
  { label: 'Resumen', icon: 'space_dashboard', to: '/admin/dashboard' },
  { label: 'Usuarios y asignaciones', icon: 'group', to: '/admin/users' },
  { label: 'Historial de cambios', icon: 'history', to: '/admin/audit' },
];
</script>
<template><PanelShell role="admin" :links="links" /></template>
