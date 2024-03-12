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

export interface FilterChain {
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
  filter_chains: FilterChain[];
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
