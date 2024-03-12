from dataclasses import dataclass, field

from api.base_request import BaseRequest
from api.base_response import BaseResponse

from wireguard.data.peer import Peer


@dataclass
class GetPeersRequest(BaseRequest):
    pass


@dataclass
class GetPeersResponse(BaseResponse):
    peers: list[Peer] = field(default_factory=list)
