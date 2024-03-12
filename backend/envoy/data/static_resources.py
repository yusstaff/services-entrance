
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from envoy.data.cluster import Cluster
from envoy.data.filter_chain import FilterChain

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/static_resources.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)

INTERNAL_BACKEND_CLUESTER_NAME: str = 'se-backend'
INTERNAL_FRONTEND_CLUESTER_NAME: str = 'se-frontend'


@dataclass
class StaticResources(object):
    filter_chains: list[FilterChain] = field(default_factory=list)
    clusters: list[Cluster] = field(default_factory=list)

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return StaticResources()
        return StaticResources([FilterChain.parse(fc) for fc in dic['filter_chains']],
                               [Cluster.parse(cluster) for cluster in dic['clusters']])

    def toDict(self) -> dict:
        static_resources = deepcopy(TEMPLATE)
        filter_chains = [filter_chain.toDict() for filter_chain in self.filter_chains]
        static_resources['listeners'][1]['filter_chains'] = filter_chains + static_resources['listeners'][1]['filter_chains']
        clusters = [cluster.toDict() for cluster in self.clusters]
        static_resources['clusters'] = static_resources['clusters'] + clusters
        return static_resources

    def validate(self) -> None:
        for chain in self.filter_chains:
            chain.validate()
        for cluster in self.clusters:
            cluster.validate()

        cluster_list = [cluster.name for cluster in self.clusters]
        if len(cluster_list) != len(set(cluster_list)):
            raise Exception('Duplicate cluster.')
        if INTERNAL_BACKEND_CLUESTER_NAME in cluster_list:
            raise Exception(f'Cannot use internal cluster {INTERNAL_BACKEND_CLUESTER_NAME}.')
        if INTERNAL_FRONTEND_CLUESTER_NAME in cluster_list:
            raise Exception(f'Cannot use internal cluster {INTERNAL_FRONTEND_CLUESTER_NAME}.')

        servers_of_chain: list[str] = []
        for chain in self.filter_chains:
            servers_of_chain.extend(chain.server_names)
            for filter in chain.filters:
                for virtual_host in filter.virtual_hosts:
                    for route in virtual_host.routes:
                        if route.cluster in cluster_list:
                            continue
                        if route.cluster != INTERNAL_BACKEND_CLUESTER_NAME:
                            continue
                        if route.cluster != INTERNAL_FRONTEND_CLUESTER_NAME:
                            continue
                        raise Exception(f'Cannot found cluster: {route.cluster}')
        if len(servers_of_chain) != len(set(servers_of_chain)):
            raise Exception('Duplicate server.')
