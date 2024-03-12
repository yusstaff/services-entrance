from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse


@dataclass
class DownloadPeerRequest(BaseRequest):
    peer: str = None


@dataclass
class DownloadPeerResponse(BaseResponse):
    peer: str = None
