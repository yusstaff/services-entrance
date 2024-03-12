from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse


@dataclass
class LoginRequest(BaseRequest):
    username: str = ''
    password: str = ''


@dataclass
class LoginResponse(BaseResponse):
    csrf_access_token: str = ''
    csrf_refresh_token: str = ''
