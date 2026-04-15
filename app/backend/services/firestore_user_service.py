from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from firebase_admin import firestore

from services.firebase_auth import get_firestore_client


USERS_COLLECTION = "users"


@dataclass(frozen=True)
class UserProfile:
    uid: str
    email: str | None
    messages_chat: int


class FirestoreUserService:
    def __init__(self) -> None:
        self._db = get_firestore_client()

    def _doc_ref(self, uid: str):
        return self._db.collection(USERS_COLLECTION).document(uid)

    def upsert_on_login(self, uid: str, email: str | None = None) -> UserProfile:
        doc_ref = self._doc_ref(uid)
        snapshot = doc_ref.get()

        if not snapshot.exists:
            payload: dict[str, Any] = {
                "messages_chat": 0,
                "created_at": firestore.SERVER_TIMESTAMP,
                "last_login_at": firestore.SERVER_TIMESTAMP,
                "last_chat_at": None,
            }
            if email:
                payload["email"] = email
            doc_ref.set(payload)
            return UserProfile(uid=uid, email=email, messages_chat=0)

        data = snapshot.to_dict() or {}
        update_payload: dict[str, Any] = {
            "last_login_at": firestore.SERVER_TIMESTAMP,
        }
        if email:
            update_payload["email"] = email
        doc_ref.set(update_payload, merge=True)

        return UserProfile(
            uid=uid,
            email=(email if email is not None else data.get("email")),
            messages_chat=int(data.get("messages_chat", 0)),
        )

    def get_user_profile(self, uid: str, email: str | None = None) -> UserProfile:
        doc_ref = self._doc_ref(uid)
        snapshot = doc_ref.get()

        if not snapshot.exists:
            return self.upsert_on_login(uid=uid, email=email)

        data = snapshot.to_dict() or {}
        return UserProfile(
            uid=uid,
            email=(data.get("email") or email),
            messages_chat=int(data.get("messages_chat", 0)),
        )

    def increment_messages_after_success(self, uid: str) -> None:
        doc_ref = self._doc_ref(uid)
        transaction = self._db.transaction()

        @firestore.transactional
        def _increment(txn):
            snapshot = doc_ref.get(transaction=txn)

            if not snapshot.exists:
                txn.set(
                    doc_ref,
                    {
                        "messages_chat": 0,
                        "created_at": firestore.SERVER_TIMESTAMP,
                        "last_login_at": firestore.SERVER_TIMESTAMP,
                        "last_chat_at": None,
                    },
                )

            txn.update(
                doc_ref,
                {
                    "messages_chat": firestore.Increment(1),
                    "last_chat_at": firestore.SERVER_TIMESTAMP,
                },
            )

        _increment(transaction)
