import { api } from 'boot/axios';
import API from 'api/auth/api';

export type ILogoutResponse = Response;

export default function logout() {
  return api.post<ILogoutResponse>(API.LOGOUT);
}
