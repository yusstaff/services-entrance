import { api } from 'boot/axios';
import API from 'api/auth/api';
import { useCsrfStore } from 'stores/csrf';

export interface IRefreshResponse extends Response {
  csrf_access_token: string;
}

export default function refresh() {
  return api.post<IRefreshResponse>(API.REFRESH, null, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().refreshToken(),
    },
  });
}
