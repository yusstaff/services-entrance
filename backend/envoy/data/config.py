from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import yaml

from envoy.data.admin import Admin
from envoy.data.static_resources import StaticResources

TEMPLATE_PATH: Path = Path('/app/backend/envoy/template/config.yml')
with TEMPLATE_PATH.open() as file:
    TEMPLATE: dict = yaml.safe_load(file)


@dataclass
class Config(object):
    static_resources: StaticResources = None
    admin: Admin = None

    @staticmethod
    def parse(dic: dict = None):
        if not dic:
            return Config()
        return Config(StaticResources.parse(dic['static_resources']), Admin.parse(dic['admin']))

    @staticmethod
    def createExample():
        static_res = StaticResources.parse()
        static_res.listeners = []
        static_res.clusters = []

        admin = Admin.parse()
        admin.access_log_path = '/tmp/admin_access.log'
        admin.port_value = 9901

        config = Config.parse()
        config.static_resources = static_res
        config.admin = admin

        return config

    def toDict(self) -> dict:
        config = deepcopy(TEMPLATE)
        config['static_resources'] = self.static_resources.toDict()
        config['admin'] = self.admin.toDict()
        return config

    def validate(self) -> None:
        self.static_resources.validate()
