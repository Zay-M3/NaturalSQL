import json
import os
from dataclasses import dataclass


def _parse_origins(value: str) -> list[str]:
    if not value:
        return []
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    firebase_credentials_path: str | None
    firebase_credentials_json: dict | None
    auth_cookie_name: str
    auth_cookie_secure: bool
    auth_cookie_max_age_seconds: int
    login_rate_limit: str
    chat_rate_limit: str
    cors_allowed_origins: list[str]


def get_settings() -> Settings:
    firebase_credentials_json: dict | None = None
    firebase_credentials_json_raw = os.getenv("FIREBASE_CREDENTIALS_JSON", "").strip()
    if firebase_credentials_json_raw:
        firebase_credentials_json = json.loads(firebase_credentials_json_raw)

    default_origins = "http://localhost:5173,http://127.0.0.1:5173"

    return Settings(
        firebase_credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH", "").strip() or None,
        firebase_credentials_json=firebase_credentials_json,
        auth_cookie_name=os.getenv("AUTH_COOKIE_NAME", "nsql_auth"),
        auth_cookie_secure=os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true",
        auth_cookie_max_age_seconds=int(os.getenv("AUTH_COOKIE_MAX_AGE_SECONDS", "3600")),
        login_rate_limit=os.getenv("LOGIN_RATE_LIMIT", "5/minute"),
        chat_rate_limit=os.getenv("CHAT_RATE_LIMIT", "5/minute"),
        cors_allowed_origins=_parse_origins(os.getenv("CORS_ALLOWED_ORIGINS", default_origins)),
    )
