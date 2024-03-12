
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import re

import yaml

from envoy.data.virtual_host import VirtualHost

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/filter.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)

MAX_REQUEST_PATTERN = re.compile(r'^\d+(?:\.\d+)?[GMK]$')


@dataclass
class Filter(object):
    virtual_hosts: list[VirtualHost] = field(default_factory=list)
    max_request_bytes: str = '16K'

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return Filter()
        max_request: str = dic['max_request_bytes']
        return Filter([VirtualHost.parse(host) for host in dic['virtual_hosts']], max_request.upper())

    def toDict(self) -> dict:
        filter = deepcopy(TEMPLATE)
        filter['typed_config']['route_config']['virtual_hosts'] = [vh.toDict() for vh in self.virtual_hosts]

        amount: float = float(self.max_request_bytes[:-1])
        unit: str = self.max_request_bytes[-1]
        if unit == 'K':
            request_size = int(amount * 1024)
        elif unit == 'M':
            request_size = int(amount * 1024 * 1024)
        elif unit == 'G':
            request_size = int(amount * 1024 * 1024 * 1024)
        else:
            request_size = int(amount)
        request_size = min(request_size, 2 ** 32 - 1)
        filter['typed_config']['http_filters'][0]['typed_config']['max_request_bytes'] = request_size

        return filter

    def validate(self) -> None:
        if not self.virtual_hosts:
            raise Exception('At least one virtual host per filter.')
        for virtual_host in self.virtual_hosts:
            virtual_host.validate()
        if not MAX_REQUEST_PATTERN.match(self.max_request_bytes):
            raise Exception(f'Wrong max request body size: {self.max_request_bytes}.')

        domains: list[str] = []
        for host in self.virtual_hosts:
            domains.extend(host.domains)
        if len(domains) != len(set(domains)):
            raise Exception('Duplicate domain.')
