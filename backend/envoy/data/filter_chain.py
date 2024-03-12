
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import re

import yaml

from envoy.data.filter import Filter

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/filter_chains.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)

DOMAIN_PATTERN = re.compile(r'^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
CERTIFICATE_PATTERN = re.compile(r'^(?:\*\.)?(?:[a-zA-Z0-9-]+\.)*[a-zA-Z]{2,}$')


@dataclass
class FilterChain(object):
    server_names: list[str] = field(default_factory=list)
    domain: str = ''
    filters: list[Filter] = field(default_factory=list)

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return FilterChain()
        return FilterChain(dic['server_names'], dic['domain'], [Filter.parse(filter) for filter in dic['filters']])

    def toDict(self) -> dict:
        filter_chain = deepcopy(TEMPLATE)
        filter_chain['transport_socket']['typed_config']['common_tls_context']['tls_certificates'][0] = {
            'certificate_chain': {
                'filename': f'/etc/letsencrypt/live/{self.domain.replace("*.", "")}/fullchain.pem',
            },
            'private_key': {
                'filename': f'/etc/letsencrypt/live/{self.domain.replace("*.", "")}/privkey.pem',
            },
        }
        filter_chain['filter_chain_match']['server_names'] = self.server_names
        filter_chain['filters'] = [filter.toDict() for filter in self.filters]
        return filter_chain

    def validate(self) -> None:
        if not self.domain:
            raise Exception('Certificate unspecified.')
        if not CERTIFICATE_PATTERN.match(self.domain):
            raise Exception(f'Wrong domain: {self.domain}')

        if not self.server_names:
            raise Exception('At least one server name per chain.')
        for server_name in self.server_names:
            if not DOMAIN_PATTERN.match(server_name):
                raise Exception(f'Wrong server name: {server_name}')

        if not self.filters:
            raise Exception('At least one filter per chain.')
        for filter in self.filters:
            filter.validate()
