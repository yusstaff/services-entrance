import { api } from 'boot/axios';
import API from 'api/wireguard/api';
import { useCsrfStore } from 'stores/csrf';

export interface IDownloadPeerRequest {
  peer: string;
}

export interface IDownloadPeerResponse extends Response {
  peer: string;
}

export default function download_peer(request: IDownloadPeerRequest) {
  return api.post<IDownloadPeerResponse>(API.DOWNLOAD_PEER, request, {
    headers: {
      'X-CSRF-TOKEN': useCsrfStore().accessToken(),
    },
  });
}
