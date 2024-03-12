from dataclasses import dataclass


@dataclass
class Subnet(object):
    address: str = ''
    cidr: int = 20
