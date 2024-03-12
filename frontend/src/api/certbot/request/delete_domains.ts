import { api } from 'boot/axios';
import API from 'api/certbot/api';
import Domain from 'api/certbot/data/domain';
import { useCsrfStore } from 'stores/csrf';

export interface IDeleteDomainsRequest {
  domains: Domain[];
}

export interface IDeleteDomainsResponse extends Response {
  domains: Domain[];
}

export default function deleteDomains(request: IDeleteDomainsRequest) {
  return api.delete<IDeleteDomainsResponse>(API.DOMAINS, {
    data: request,
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
