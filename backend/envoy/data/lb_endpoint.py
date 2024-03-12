from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import yaml

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/lb_endpoint.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)


@dataclass
class LbEndpoint(object):
    address: str = ''
    port_value: int = 443

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return LbEndpoint()
        return LbEndpoint(dic['address'], int(dic['port_value']))

    def toDict(self) -> dict:
        endpoint = deepcopy(TEMPLATE)
        endpoint['endpoint']['address']['socket_address']['address'] = self.address
        endpoint['endpoint']['address']['socket_address']['port_value'] = self.port_value
        return endpoint

    def validate(self) -> None:
        if not self.address:
            raise Exception('Empty address.')
        if self.port_value < 0 or self.port_value > 65535:
            raise Exception('Port: 0-65535')
