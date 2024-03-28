from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import yaml

from envoy.data.listener import Listener, ListenerType

TCP_TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/listener_tcp.yml')
with TCP_TEMPLATE_PATH.open() as file:
    TCP_TEMPLATE: dict = yaml.safe_load(file)
UDP_TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/listener_udp.yml')
with UDP_TEMPLATE_PATH.open() as file:
    UDP_TEMPLATE: dict = yaml.safe_load(file)


@dataclass
class ListenerTCPUDP(Listener):
    port_value: int = 12345
    cluster: str = ''

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return ListenerTCPUDP()
        return ListenerTCPUDP(dic['type'], int(dic['port_value']), dic['cluster'])

    def toDict(self) -> list[dict]:
        listeners: list[dict] = []
        if self.type == ListenerType.TCPUDP.value or self.type == ListenerType.TCP.value:
            tcp_listener = deepcopy(TCP_TEMPLATE)
            tcp_listener['address']['socket_address']['port_value'] = self.port_value
            tcp_listener['filter_chains'][0]['filters'][0]['typed_config']['cluster'] = self.cluster
            listeners.append(tcp_listener)
        if self.type == ListenerType.TCPUDP.value or self.type == ListenerType.UDP.value:
            udp_listener = deepcopy(UDP_TEMPLATE)
            udp_listener['address']['socket_address']['port_value'] = self.port_value
            udp_listener['listener_filters'][0]['typed_config']['cluster'] = self.cluster
            listeners.append(udp_listener)
        return listeners

    def validate(self) -> None:
        if self.port_value < 0 or self.port_value > 65535:
            raise Exception('Port: 0-65535.')
        if not self.cluster:
            raise Exception(f'Wrong cluster: {self.cluster}')
