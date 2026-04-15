from typing import Any

import firebase_admin
from firebase_admin import auth, credentials, firestore

from config import get_settings


_firebase_initialized = False


def _initialize_firebase_admin() -> None:
    global _firebase_initialized
    if _firebase_initialized:
        return

    try:
        firebase_admin.get_app()
        _firebase_initialized = True
        return
    except ValueError:
        pass

    settings = get_settings()

    if not settings.firebase_credentials_path and not settings.firebase_credentials_json:
        raise RuntimeError(
            "Firebase Admin credentials are required. Set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON."
        )

    if settings.firebase_credentials_json:
        cred = credentials.Certificate(settings.firebase_credentials_json)
    else:
        cred = credentials.Certificate(settings.firebase_credentials_path)

    firebase_admin.initialize_app(cred)
    _firebase_initialized = True


def verify_firebase_id_token(id_token: str) -> dict[str, Any]:
    _initialize_firebase_admin()
    return auth.verify_id_token(id_token)


def get_firestore_client() -> firestore.Client:
    _initialize_firebase_admin()
    return firestore.client()
