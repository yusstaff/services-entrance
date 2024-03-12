from dataclasses import dataclass, field

from api.base_request import BaseRequest
from api.base_response import BaseResponse
from wireguard.data.peer import Peer


@dataclass
class AddPeersRequest(BaseRequest):
    peers: list[str] = field(default_factory=list)


@dataclass
class AddPeersResponse(BaseResponse):
    peers: list[Peer] = field(default_factory=list)
