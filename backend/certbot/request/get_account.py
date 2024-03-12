from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse


@dataclass
class GetAccountRequest(BaseRequest):
    pass


@dataclass
class GetAccountResponse(BaseResponse):
    email: str = ''
