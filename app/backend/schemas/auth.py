from pydantic import BaseModel


class LoginRequest(BaseModel):
    idToken: str


class AuthStatusResponse(BaseModel):
    uid: str
    email: str | None = None


class AuthMeResponse(BaseModel):
    uid: str
    email: str | None = None
    messages_chat: int
