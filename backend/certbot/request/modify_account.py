from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse


@dataclass
class ModifyAccountRequest(BaseRequest):
    email: str = ''
    api_key: str = ''


@dataclass
class ModifyAccountResponse(BaseResponse):
    email: str = ''
