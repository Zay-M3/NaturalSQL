from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from config import get_settings
from dependencies.auth import get_current_user
from schemas.auth import AuthMeResponse, AuthStatusResponse, LoginRequest
from services.firebase_auth import verify_firebase_id_token
from services.firestore_user_service import FirestoreUserService
from services.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])
_settings = get_settings()
_user_service = FirestoreUserService()


@router.post("/login", response_model=AuthStatusResponse)
@limiter.limit(_settings.login_rate_limit)
def login(request: Request, payload: LoginRequest, response: Response) -> AuthStatusResponse:
    try:
        token_data = verify_firebase_id_token(payload.idToken)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase ID token")

    profile = _user_service.upsert_on_login(uid=token_data["uid"], email=token_data.get("email"))

    response.set_cookie(
        key=_settings.auth_cookie_name,
        value=payload.idToken,
        httponly=True,
        samesite="lax",
        secure=_settings.auth_cookie_secure,
        max_age=_settings.auth_cookie_max_age_seconds,
    )

    return AuthStatusResponse(uid=profile.uid, email=profile.email)


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=_settings.auth_cookie_name,
        httponly=True,
        samesite="lax",
        secure=_settings.auth_cookie_secure,
    )
    return {"status": "ok"}


@router.get("/me", response_model=AuthMeResponse)
def me(current_user: dict[str, Any] = Depends(get_current_user)) -> AuthMeResponse:
    profile = _user_service.get_user_profile(uid=current_user["uid"], email=current_user.get("email"))
    return AuthMeResponse(uid=profile.uid, email=profile.email, messages_chat=profile.messages_chat)
