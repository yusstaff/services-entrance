from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse


@dataclass
class VerifyRequest(BaseRequest):
    pass


@dataclass
class VerifyResponse(BaseResponse):
    verified: bool = False
