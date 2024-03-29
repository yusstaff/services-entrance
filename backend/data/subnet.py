from dataclasses import dataclass
import os
from pathlib import Path
import re

import yaml

SUBNET_ADDRESS_PATTERN = re.compile(
    r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')


@dataclass
class Subnet(object):
    address: str = ''
    cidr: int = 20


def read_subnets(config_path: Path) -> list[Subnet]:
    subnets: list[Subnet] = []
    if config_path.exists():
        with config_path.open() as file:
            config_data: list[dict] = yaml.safe_load(file)
            if config_data:
                for subnet in config_data:
                    subnets.append(Subnet(subnet['address'], int(subnet['cidr'])))
    return subnets


def save_subnets(config_path: Path, subnets: list[Subnet]) -> None:
    with config_path.open('w') as file:
        subnets = [subnet.__dict__ for subnet in subnets]
        yaml.safe_dump(subnets, file)


def validate_subnets(subnets: list[Subnet]) -> str | None:
    for subnet in subnets:
        if not SUBNET_ADDRESS_PATTERN.match(subnet.address):
            return f'Wrong subnet address {subnet.address}/{subnet.cidr}.'
        elif subnet.cidr < 16 or subnet.cidr > 32:
            return f'Wrong subnet CIDR {subnet.address}/{subnet.cidr}. CIDR: 16-32.'
    return None


def set_subnets(subnets: list[Subnet], container_name: str) -> None:
    for subnet in subnets:
        cmd = (f'next_hop_ip=$(dig +short {container_name}) && '
               f'ip route replace {subnet.address}/{subnet.cidr} via $next_hop_ip dev eth0')
        os.system(cmd)


def unset_subnets(subnets: list[Subnet], container_name: str) -> None:
    for subnet in subnets:
        cmd = (f'next_hop_ip=$(dig +short {container_name}) && '
               f'ip route del {subnet.address}/{subnet.cidr}')
        os.system(cmd)
