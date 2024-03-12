from dataclasses import dataclass, field

from api.base_request import BaseRequest
from api.base_response import BaseResponse
from certbot.data.domain import Domain


@dataclass
class RemoveDomainsRequest(BaseRequest):
    domains: list[dict] = field(default_factory=list)


@dataclass
class RemoveDomainsResponse(BaseResponse):
    domains: list[Domain] = field(default_factory=list)
