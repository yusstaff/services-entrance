import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';
import qs from 'qs';
import { Notify } from 'quasar';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: AxiosInstance;
  }
}

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({
  baseURL:
    process.env.NODE_ENV === 'production'
      ? `${window.location.protocol}//${window.location.hostname}/`
      : `${window.location.protocol}//${window.location.hostname}:5571/`,
  responseType: 'json',
  paramsSerializer: (params) => qs.stringify(params, { arrayFormat: 'repeat' }),
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default boot(({ app, router }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API

  api.interceptors.response.use(
    (response) => {
      if (response.data.status !== 0) {
        Notify.create({
          message: response.data.message,
          color: 'red',
          position: 'top',
          timeout: response.data.status * 1000,
        });
        return Promise.reject(response);
      }
      return response;
    },
    (error) => {
      if (error.response) {
        if (error.response.status === 401 || error.response.status === 422) {
          router.push('/login');
        }
        console.error('An error occurred:', error.response.status);
      } else if (error.request) {
        console.error('No response received for the request.');
      } else {
        console.error('Error setting up the request:', error.message);
      }

      return Promise.reject(error);
    }
  );
});

export { api };
