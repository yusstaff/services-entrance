from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse


@dataclass
class RefreshRequest(BaseRequest):
    pass


@dataclass
class RefreshResponse(BaseResponse):
    csrf_access_token: str = ''
