from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import re

import yaml

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/route.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)

PREFIX_PATTERN = re.compile(r'^/[a-zA-Z/-]*$')


@dataclass
class Route(object):
    prefix: str = ''
    cluster: str = ''
    host_rewrite_literal: str = ''

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return Route()
        return Route(dic['prefix'], dic['cluster'], dic['host_rewrite_literal'])

    def toDict(self) -> dict:
        route = deepcopy(TEMPLATE)
        route['match']['prefix'] = self.prefix
        route['route']['cluster'] = self.cluster
        if self.host_rewrite_literal:
            route['route']['host_rewrite_literal'] = self.host_rewrite_literal
        else:
            dic: dict = route['route']
            dic.pop('host_rewrite_literal')

        return route

    def validate(self) -> None:
        if not PREFIX_PATTERN.match(self.prefix):
            raise Exception(f'Wrong prefix: {self.prefix}')
        if not self.cluster:
            raise Exception(f'Wrong cluster: {self.cluster}')
