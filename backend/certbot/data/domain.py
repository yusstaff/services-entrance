
from dataclasses import dataclass


@dataclass
class Domain(object):
    domain: str = ''
    hasCertificate: bool = False
