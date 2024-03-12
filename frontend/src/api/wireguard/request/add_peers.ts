import { api } from 'boot/axios';
import API from 'api/wireguard/api';
import Peer from 'api/wireguard/data/peer';
import { useCsrfStore } from 'stores/csrf';

export interface IAddPeersRequest {
  peers: string[];
}

export interface IAddPeersResponse extends Response {
  peers: Peer[];
}

export default function addPeers(request: IAddPeersRequest) {
  return api.post<IAddPeersResponse>(API.PEERS, request, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
