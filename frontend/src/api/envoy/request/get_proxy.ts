import { api } from 'boot/axios';
import API from 'api/envoy/api';
import Config from 'api/envoy/data/config';

export interface IGetProxyResponse extends Response {
  config: Config;
}

export default function getProxy() {
  return api.get<IGetProxyResponse>(API.PROXY);
}
