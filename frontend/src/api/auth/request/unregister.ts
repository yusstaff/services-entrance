import { api } from 'boot/axios';
import API from 'api/auth/api';
import { useCsrfStore } from 'stores/csrf';

export type IUnregisterResponse = Response;

export default function logout() {
  return api.delete<IUnregisterResponse>(API.UNREGISTER, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
