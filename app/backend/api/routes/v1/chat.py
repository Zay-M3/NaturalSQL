from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from controller.chat_controller import ChatController
from dependencies.auth import get_current_user
from schemas.chat import RequestMessage
from config import get_settings
from services.firestore_user_service import FirestoreUserService
from services.limiter import limiter

router = APIRouter(prefix="/chat", tags=["chat"])

_settings = get_settings()
_user_service = FirestoreUserService()

@router.post("/message")
@limiter.limit(_settings.chat_rate_limit)
async def send_message(
    request: Request,
    payload: RequestMessage,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    profile = _user_service.get_user_profile(uid=current_user["uid"], email=current_user.get("email"))
    if profile.messages_chat >= 10:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat quota reached",
        )

    chat_controller = ChatController()
    response = await chat_controller.process_message(
        message=payload.message,
        on_success=lambda: _user_service.increment_messages_after_success(current_user["uid"]),
    )
    return response
