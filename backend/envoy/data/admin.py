from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import yaml

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/admin.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)


@dataclass
class Admin(object):
    access_log_path: str = ''
    port_value: int = 9901

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return Admin()
        return Admin(dic['access_log_path'], dic['port_value'])

    def toDict(self) -> dict:
        admin = deepcopy(TEMPLATE)
        admin['access_log_path'] = self.access_log_path
        admin['address']['socket_address']['port_value'] = self.port_value
        return admin
