import { defineStore } from 'pinia';

export const useCsrfStore = defineStore('csrf', {
  state: () => ({}),
  getters: {},
  actions: {
    accessToken: () => {
      const cookies: string[] = document.cookie.split('; ');
      for (let i = 0; i < cookies.length; i++) {
        const cookiePair: string[] = cookies[i].split('=');
        if (cookiePair[0] === 'csrf_access_token') {
          return decodeURIComponent(cookiePair[1]);
        }
      }
      return '';
    },
    refreshToken: () => {
      const cookies: string[] = document.cookie.split('; ');
      for (let i = 0; i < cookies.length; i++) {
        const cookiePair: string[] = cookies[i].split('=');
        if (cookiePair[0] === 'csrf_refresh_token') {
          return decodeURIComponent(cookiePair[1]);
        }
      }
      return '';
    },
  },
});
