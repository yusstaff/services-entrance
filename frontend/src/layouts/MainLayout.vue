<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title> Services Entrance </q-toolbar-title>
        <q-space></q-space>

        <q-btn color="grey" icon="logout" @click="onLogout">Logout</q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header> Menu </q-item-label>

        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import EssentialLink, {
  EssentialLinkProps,
} from 'components/EssentialLink.vue';
import logout from 'api/auth/request/logout';
import { useRouter } from 'vue-router';

const router = useRouter();

const essentialLinks: EssentialLinkProps[] = [
  {
    title: 'Domain & Certificate',
    icon: 'public',
    link: '/Certbot',
    level: 0,
    separate: true,
  },
  {
    title: 'VPN',
    icon: 'cloud_queue',
    clickable: false,
    level: 0,
    separate: true,
  },
  {
    title: 'Wireguard',
    icon: 'cloud_queue',
    link: '/wireguard',
    level: 1,
  },
  {
    title: 'Openvpn',
    icon: 'cloud_queue',
    link: '/openvpn',
    level: 1,
  },
  {
    title: 'Proxy',
    icon: 'sync_alt',
    clickable: false,
    level: 0,
    separate: true,
  },
  {
    title: 'Inbound',
    icon: 'keyboard_tab',
    link: '/envoy-listener',
    level: 1,
  },
  {
    title: 'Outbound',
    icon: 'start',
    link: '/envoy-cluster',
    level: 1,
  },
  {
    title: 'Settings',
    icon: 'settings',
    link: '/settings',
    level: 0,
    separate: true,
  },
];

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function onLogout() {
  logout().then(() => {
    router.push('/login');
  });
}
</script>
src/api/auth/request/logout
