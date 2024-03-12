import { api } from 'boot/axios';
import API from 'api/openvpn/api';
import Subnet from 'api/openvpn/data/subnet';
import { useCsrfStore } from 'stores/csrf';

export interface IModifySubnetsRequest {
  subnets: Subnet[];
}

export interface IModifySubnetsResponse extends Response {
  subnets: Subnet[];
}

export default function addSubnets(request: IModifySubnetsRequest) {
  return api.post<IModifySubnetsResponse>(API.SUBNETS, request, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
