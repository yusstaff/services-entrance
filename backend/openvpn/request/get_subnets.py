from dataclasses import dataclass, field

from api.base_request import BaseRequest
from api.base_response import BaseResponse
from openvpn.data.subnet import Subnet


@dataclass
class GetSubnetsRequest(BaseRequest):
    pass


@dataclass
class GetSubnetsResponse(BaseResponse):
    subnets: list[Subnet] = field(default_factory=list)
