import { api } from 'boot/axios';
import API from 'api/certbot/api';
import { useCsrfStore } from 'stores/csrf';

export interface IModifyAccountRequest {
  email: string;
  api_key: string;
}

export interface IModifyAccountResponse extends Response {
  email: string;
}

export default function modifyAccount(request: IModifyAccountRequest) {
  return api.post<IModifyAccountResponse>(API.ACCOUNT, request, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
