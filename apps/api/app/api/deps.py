from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.security import RequestContext, decode_internal_token
from app.models.entities import Organization, User


bearer_scheme = HTTPBearer(auto_error=False)


def get_settings_dep() -> Settings:
    return get_settings()


def get_request_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> RequestContext:
    if credentials:
        try:
            payload = decode_internal_token(credentials.credentials, settings)
            return RequestContext(
                user_id=payload["user_id"],
                org_id=payload["org_id"],
                role=payload.get("role", "editor"),
                email=payload.get("email", ""),
                name=payload.get("name", "Editor"),
            )
        except Exception as exc:  # pragma: no cover - protective boundary
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if not settings.allow_demo_auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    organization = db.scalar(select(Organization).where(Organization.slug == settings.default_org_slug))
    user = db.scalar(select(User).where(User.email == "editor@datadrivendaily.local"))
    if organization is None or user is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Seed data missing")
    return RequestContext(
        user_id=user.id,
        org_id=organization.id,
        role=user.role,
        email=user.email,
        name=user.name,
    )

