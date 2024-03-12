from dataclasses import dataclass


@dataclass
class BaseResponse(object):
    status: int = 0
    message: str = ''
