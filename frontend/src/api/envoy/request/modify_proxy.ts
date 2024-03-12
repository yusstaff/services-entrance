import { api } from 'boot/axios';
import API from 'api/envoy/api';
import Config from 'api/envoy/data/config';
import { useCsrfStore } from 'stores/csrf';

export interface IModifyProxyRequest {
  config: Config;
}

export type IModifyProxyResponse = Response;

export default function modifyProxy(request: IModifyProxyRequest) {
  return api.post<IModifyProxyResponse>(API.PROXY, request, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
