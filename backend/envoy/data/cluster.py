from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import re

import yaml

from envoy.data.endpoint import Endpoint

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/cluster.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)

NAME_PATTERN = re.compile('^[a-zA-Z0-9_-]{3,20}')
PROTOCAL_LIST = ['HTTP/1.1', 'HTTPS/1.1', 'HTTP/2', 'TCP/UDP']


@dataclass
class Cluster(object):
    name: str = ''
    endpoints: list[Endpoint] = field(default_factory=list)
    protocol: str = 'HTTP/2'

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return Cluster()
        return Cluster(dic['name'], [Endpoint.parse(endpoint) for endpoint in dic['endpoints']], dic['protocol'])

    def toDict(self) -> dict:
        cluster = deepcopy(TEMPLATE)
        cluster['name'] = self.name
        cluster['load_assignment']['cluster_name'] = self.name
        cluster['load_assignment']['endpoints'] = [endpoint.toDict() for endpoint in self.endpoints]
        if self.protocol == 'HTTP/1.1' or self.protocol == 'TCP/UDP':
            cluster.pop('transport_socket')
            cluster.pop('http2_protocol_options')
        elif self.protocol == 'HTTPS/1.1':
            cluster.pop('http2_protocol_options')
        return cluster

    def validate(self) -> None:
        if not NAME_PATTERN.match(self.name):
            raise Exception('Cluster name: 3-20 character, a-z, A-Z, 0-9, _-.')

        if not self.endpoints:
            raise Exception('At least one endpoint per cluster')
        for endpoint in self.endpoints:
            endpoint.validate()

        if self.protocol not in PROTOCAL_LIST:
            raise Exception(f'Supported protocol: {PROTOCAL_LIST}')
