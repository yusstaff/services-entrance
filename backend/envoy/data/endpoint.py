from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from envoy.data.lb_endpoint import LbEndpoint

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/endpoint.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)


@dataclass
class Endpoint(object):
    lb_endpoints: list[LbEndpoint] = field(default_factory=list)

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return Endpoint()
        return Endpoint([LbEndpoint.parse(endpoint) for endpoint in dic['lb_endpoints']])

    def toDict(self) -> dict:
        lb_endpoints = deepcopy(TEMPLATE)
        lb_endpoints['lb_endpoints'] = [endpoint.toDict() for endpoint in self.lb_endpoints]
        return lb_endpoints

    def validate(self) -> None:
        if not self.lb_endpoints:
            raise Exception('At least one lb_endpoint per endpoint.')
        for lb_endpoint in self.lb_endpoints:
            lb_endpoint.validate()
