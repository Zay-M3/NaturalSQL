from typing import Any

from pydantic import BaseModel, Field


class RequestMessage(BaseModel):
    message: str = Field(..., min_length=2, max_length=4000, description="The user's message to the chatbot")
    
class ResponseMessage(BaseModel):
    response: dict[str, Any]