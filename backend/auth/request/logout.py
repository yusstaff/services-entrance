from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse


@dataclass
class LogoutRequest(BaseRequest):
    pass


@dataclass
class LogoutResponse(BaseResponse):
    pass
