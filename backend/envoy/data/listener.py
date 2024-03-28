from dataclasses import dataclass
from enum import Enum


class ListenerType(Enum):
    HTTP = 'HTTP/HTTPS'
    TCPUDP = 'TCP/UDP'
    TCP = 'TCP'
    UDP = 'UDP'


@dataclass
class Listener(object):
    type: str = ListenerType.HTTP.value

    def validate(self) -> None:
        pass
