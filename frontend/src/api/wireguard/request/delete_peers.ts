import { api } from 'boot/axios';
import API from 'api/wireguard/api';
import Peer from 'api/wireguard/data/peer';
import { useCsrfStore } from 'stores/csrf';

export interface IDeletePeersRequest {
  peers: Peer[];
}

export interface IDeletePeersResponse extends Response {
  peers: Peer[];
}

export default function deletePeers(request: IDeletePeersRequest) {
  return api.delete<IDeletePeersResponse>(API.PEERS, {
    data: request,
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
