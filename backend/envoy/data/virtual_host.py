from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import re

import yaml

from envoy.data.route import Route

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/virtual_host.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)

NAME_PATTERN = re.compile(r'[a-zA-Z0-9_-]{4,}')
DOMAIN_PATTERN = re.compile(r'^((\*\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|\*)$')


@dataclass
class VirtualHost(object):
    name: str = ''
    domains: list[str] = field(default_factory=list)
    routes: list[Route] = field(default_factory=list)

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return VirtualHost()
        return VirtualHost(dic['name'], dic['domains'], [Route.parse(route) for route in dic['routes']])

    def toDict(self) -> dict:
        virtual_host = deepcopy(TEMPLATE)
        virtual_host['name'] = self.name
        virtual_host['domains'] = self.domains
        virtual_host['routes'] = [route.toDict() for route in self.routes]
        return virtual_host

    def validate(self) -> None:
        if not NAME_PATTERN.match(self.name):
            raise Exception('Virtual host name: at least 4 characters, a-z, A-Z, 0-9, _-.')

        if not self.domains:
            raise Exception('At least one domain per virtual host.')
        for domain in self.domains:
            if not DOMAIN_PATTERN.match(domain):
                raise Exception(f'Wrong domain: {domain}')

        if not self.routes:
            raise Exception('At least one route per virtual host.')
        for route in self.routes:
            route.validate()
