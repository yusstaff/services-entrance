import { api } from 'boot/axios';
import API from 'api/auth/api';

export interface ILoginRequest {
  username: string;
  password: string;
}

export interface ILoginResponse extends Response {
  csrf_access_token: string;
  csrf_refresh_token: string;
}

export default function login(request: ILoginRequest) {
  return api.post<ILoginResponse>(API.LOGIN, request);
}
