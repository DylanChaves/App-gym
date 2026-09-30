<script setup lang="ts">
import PanelShell from '../components/navigation/PanelShell.vue';
const links = [{ label: 'Mis clientes', icon: 'group', to: '/coach/dashboard' }];
</script>
<template><PanelShell role="coach" :links="links" /></template>
