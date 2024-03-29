import { api } from 'boot/axios';
import API from 'api/wireguard/api';
import Subnet from 'api/data/subnet';
import { useCsrfStore } from 'stores/csrf';

export interface IModifySubnetsRequest {
  subnets: Subnet[];
}

export interface IModifySubnetsResponse extends Response {
  subnets: Subnet[];
}

export default function modifySubnets(request: IModifySubnetsRequest) {
  return api.post<IModifySubnetsResponse>(API.SUBNETS, request, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
