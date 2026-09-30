<script setup lang="ts">
import PanelShell from '../components/navigation/PanelShell.vue';
const links = [
  { label: 'Inicio', icon: 'home', to: '/member/home' },
  { label: 'Mi perfil', icon: 'person', to: '/member/profile' },
];
</script>
<template><PanelShell role="member" :links="links" /></template>
