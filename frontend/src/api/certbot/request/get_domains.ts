import { api } from 'boot/axios';
import API from 'api/certbot/api';
import Domain from 'api/certbot/data/domain';

export interface IGetDomainsResponse extends Response {
  domains: Domain[];
}

export default function getDomains() {
  return api.get<IGetDomainsResponse>(API.DOMAINS);
}
