import { api } from 'boot/axios';
import API from 'api/certbot/api';

export interface IGetAccountResponse extends Response {
  email: string;
}

export default function getAccount() {
  return api.get<IGetAccountResponse>(API.ACCOUNT);
}
