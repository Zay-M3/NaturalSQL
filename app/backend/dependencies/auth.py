from typing import Any

from fastapi import Cookie, HTTPException, status

from config import get_settings
from services.firebase_auth import verify_firebase_id_token
from firebase_admin.auth import ExpiredIdTokenError, InvalidIdTokenError, RevokedIdTokenError

TOKEN_VALIDATION_EXCEPTIONS = (
    ValueError,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)

def get_current_user(
    auth_cookie: str | None = Cookie(default=None, alias=get_settings().auth_cookie_name),
) -> dict[str, Any]:
    if not auth_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        token_data = verify_firebase_id_token(auth_cookie)
    except TOKEN_VALIDATION_EXCEPTIONS as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from err

    return {
        "uid": token_data.get("uid"),
        "email": token_data.get("email"),
        "token": token_data,
    }
