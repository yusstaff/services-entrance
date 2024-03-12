from dataclasses import dataclass

from api.base_request import BaseRequest
from api.base_response import BaseResponse
from envoy.data.config import Config


@dataclass
class ModifyProxyRequest(BaseRequest):
    config: Config = None


@dataclass
class ModifyProxyResponse(BaseResponse):
    pass
