from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jwt

from app.core.config import Settings


@dataclass(slots=True)
class RequestContext:
    user_id: str
    org_id: str
    role: str
    email: str
    name: str


def create_internal_token(payload: dict[str, Any], settings: Settings) -> str:
    return jwt.encode(payload, settings.jwt_shared_secret, algorithm="HS256")


def decode_internal_token(token: str, settings: Settings) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_shared_secret, algorithms=["HS256"])

