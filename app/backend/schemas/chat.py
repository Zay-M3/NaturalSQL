from typing import Any

from pydantic import BaseModel


class RequestMessage(BaseModel):
    message: str
    
class ResponseMessage(BaseModel):
    response: dict[str, Any]