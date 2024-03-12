from dataclasses import dataclass, field

from api.base_request import BaseRequest
from api.base_response import BaseResponse
from openvpn.data.subnet import Subnet


@dataclass
class ModifySubnetsRequest(BaseRequest):
    subnets: list[Subnet] = field(default_factory=list)

    def parse(self, jso: dict) -> None:
        self.subnets = [Subnet(subnet['address'], int(subnet['cidr'])) for subnet in jso['subnets']]


@dataclass
class ModifySubnetsResponse(BaseResponse):
    subnets: list[Subnet] = field(default_factory=list)
