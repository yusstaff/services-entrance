
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from envoy.data.cluster import Cluster
from envoy.data.listener import Listener, ListenerType
from envoy.data.listener_http import ListenerHTTP
from envoy.data.listener_tcp_udp import ListenerTCPUDP

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/static_resources.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)

INTERNAL_BACKEND_CLUESTER_NAME: str = 'se-backend'
INTERNAL_FRONTEND_CLUESTER_NAME: str = 'se-frontend'


@dataclass
class StaticResources(object):
    listeners: list[Listener] = field(default_factory=list)
    clusters: list[Cluster] = field(default_factory=list)

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return StaticResources()

        listeners: list[Listener] = []
        for listener in dic['listeners']:
            listener_type: str = listener['type']
            if ListenerType.HTTP.value == listener_type:
                listeners.append(ListenerHTTP.parse(listener))
            elif (ListenerType.TCPUDP.value == listener_type
                  or ListenerType.TCP.value == listener_type
                  or ListenerType.UDP.value == listener_type):
                listeners.append(ListenerTCPUDP.parse(listener))

        clusters: list[Cluster] = [Cluster.parse(cluster) for cluster in dic['clusters']]

        return StaticResources(listeners, clusters)

    def toDict(self) -> dict:
        static_resources = deepcopy(TEMPLATE)

        http_listeners: list[ListenerHTTP] = [
            listener for listener in self.listeners if ListenerType.HTTP.value == listener.type]
        http_filter_chains = [listener.toDict()['filter_chains'][0] for listener in http_listeners]
        static_resources['listeners'][1]['filter_chains'] = (
            http_filter_chains + static_resources['listeners'][1]['filter_chains'])

        tcp_udp_listeners: list[ListenerTCPUDP] = [listener for listener in self.listeners if (
            ListenerType.TCPUDP.value == listener.type
            or ListenerType.TCP.value == listener.type
            or ListenerType.UDP.value == listener.type)]
        static_resources['listeners'] = (static_resources['listeners'] +
                                         [listener
                                          for listeners in tcp_udp_listeners
                                          for listener in listeners.toDict()])

        clusters = [cluster.toDict() for cluster in self.clusters]
        static_resources['clusters'] = static_resources['clusters'] + clusters

        return static_resources

    def validate(self) -> None:
        for listener in self.listeners:
            listener.validate()
        for cluster in self.clusters:
            cluster.validate()

        cluster_list = [cluster.name for cluster in self.clusters]
        if len(cluster_list) != len(set(cluster_list)):
            raise Exception('Duplicate cluster.')
        if INTERNAL_BACKEND_CLUESTER_NAME in cluster_list:
            raise Exception(f'Cannot use internal cluster {INTERNAL_BACKEND_CLUESTER_NAME}.')
        if INTERNAL_FRONTEND_CLUESTER_NAME in cluster_list:
            raise Exception(f'Cannot use internal cluster {INTERNAL_FRONTEND_CLUESTER_NAME}.')
        cluster_list.append(INTERNAL_BACKEND_CLUESTER_NAME)
        cluster_list.append(INTERNAL_FRONTEND_CLUESTER_NAME)

        http_servers: list[str] = []
        http_listeners: list[ListenerHTTP] = [
            listener for listener in self.listeners if ListenerType.HTTP.value == listener.type]
        for listener in http_listeners:
            http_servers.extend(listener.server_names)
            for filter in listener.filters:
                for virtual_host in filter.virtual_hosts:
                    for route in virtual_host.routes:
                        if route.cluster in cluster_list:
                            continue
                        raise Exception(f'Cannot found cluster: {route.cluster}')
        if len(http_servers) != len(set(http_servers)):
            raise Exception('Duplicate server.')

        tcp_listeners: list[ListenerTCPUDP] = [listener for listener in self.listeners if (
            ListenerType.TCPUDP.value == listener.type
            or ListenerType.TCP.value == listener.type)]
        tcp_port: list[int] = [listener.port_value for listener in tcp_listeners]
        if len(tcp_port) != len(set(tcp_port)):
            raise Exception('Duplicate TCP port.')

        udp_listeners: list[ListenerTCPUDP] = [listener for listener in self.listeners if (
            ListenerType.TCPUDP.value == listener.type
            or ListenerType.UDP.value == listener.type)]
        udp_port: list[int] = [listener.port_value for listener in udp_listeners]
        if len(udp_port) != len(set(udp_port)):
            raise Exception('Duplicate UDP port.')

        for listener in tcp_listeners + udp_listeners:
            if listener.cluster in cluster_list:
                continue
            raise Exception(f'Cannot found cluster: {listener.cluster}')
