from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse
from envoy.data.config import Config


@dataclass
class GetProxyRequest(BaseRequest):
    pass


@dataclass
class GetProxyResponse(BaseResponse):
    config: Config = None
