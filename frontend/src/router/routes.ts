import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/login/',
    component: () => import('pages/auth/LoginPage.vue'),
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'wireguard',
        component: () => import('pages/wireguard/WireguardConfiguration.vue'),
      },
      {
        path: 'openvpn',
        component: () => import('pages/openvpn/OpenvpnConfiguration.vue'),
      },
      {
        path: 'certbot',
        component: () => import('pages/certbot/CertbotConfiguration.vue'),
      },
      {
        path: 'envoy-listener',
        component: () => import('pages/envoy/EnvoyListenerConfiguration.vue'),
      },
      {
        path: 'envoy-cluster',
        component: () => import('pages/envoy/EnvoyClusterConfiguration.vue'),
      },
      {
        path: 'settings',
        component: () => import('pages/setting/SettingsPage.vue'),
      },
      {
        path: '',
        component: () => import('pages/certbot/CertbotConfiguration.vue'),
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
