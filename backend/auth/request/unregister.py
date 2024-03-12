from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse


@dataclass
class UnregisterRequest(BaseRequest):
    pass


@dataclass
class UnregisterResponse(BaseResponse):
    pass
