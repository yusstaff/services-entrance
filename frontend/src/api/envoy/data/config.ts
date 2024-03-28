export interface Route {
  prefix: string;
  cluster: string;
  host_rewrite_literal: string;
}

export interface VirtualHost {
  name: string;
  domains: string[];
  routes: Route[];
}

export interface Filter {
  virtual_hosts: VirtualHost[];
  max_request_bytes: string;
}

export interface Listener {
  type: string;
}

export interface ListenerHTTP extends Listener {
  server_names: string[];
  domain: string;
  filters: Filter[];
}

export interface LbEndpoint {
  address: string;
  port_value: number;
}

export interface Endpoint {
  lb_endpoints: LbEndpoint[];
}

export interface Cluster {
  name: string;
  endpoints: Endpoint[];
  protocol: string;
}

export interface StaticResources {
  listeners: Listener[];
  clusters: Cluster[];
}

export interface Admin {
  access_log_path: string;
  port_value: number;
}

export default interface Config {
  static_resources: StaticResources;
  admin: Admin;
}
