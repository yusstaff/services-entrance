
from dataclasses import dataclass


@dataclass
class Peer(object):
    name: str = ''
    address: str = ''
    public_key: str = ''
