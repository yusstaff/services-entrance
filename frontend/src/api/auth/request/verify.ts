import { api } from 'boot/axios';
import API from 'api/auth/api';

export interface IVerifyResponse extends Response {
  verified: boolean;
}

export default function verify() {
  return api.get<IVerifyResponse>(API.VERIFY);
}
