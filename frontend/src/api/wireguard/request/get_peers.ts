import { api } from 'boot/axios';
import API from 'api/wireguard/api';
import Peer from 'api/wireguard/data/peer';

export interface IGetPeersResponse extends Response {
  peers: Peer[];
}

export default function getPeers() {
  return api.get<IGetPeersResponse>(API.PEERS);
}
