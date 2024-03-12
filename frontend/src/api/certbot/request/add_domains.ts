import { api } from 'boot/axios';
import API from 'api/certbot/api';
import Domain from 'api/certbot/data/domain';
import { useCsrfStore } from 'stores/csrf';

export interface IAddDomainsRequest {
  domains: string[];
}

export interface IAddDomainsResponse extends Response {
  domains: Domain[];
}

export default function addDomains(request: IAddDomainsRequest) {
  return api.post<IAddDomainsResponse>(API.DOMAINS, request, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
