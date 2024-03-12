from dataclasses import dataclass, field

from api.base_request import BaseRequest
from api.base_response import BaseResponse
from certbot.data.domain import Domain


@dataclass
class GetDomainsRequest(BaseRequest):
    pass


@dataclass
class GetDomainsResponse(BaseResponse):
    domains: list[Domain] = field(default_factory=list)
