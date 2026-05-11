from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_context
from app.core.security import RequestContext
from app.models.entities import NewsletterSnapshot
from app.schemas.newsletters import NewsletterSnapshotRead


router = APIRouter(prefix="/newsletters", tags=["newsletters"])


@router.get("", response_model=list[NewsletterSnapshotRead])
def list_newsletters(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[NewsletterSnapshot]:
    return db.scalars(
        select(NewsletterSnapshot)
        .where(NewsletterSnapshot.org_id == context.org_id)
        .order_by(NewsletterSnapshot.created_at.desc())
    ).all()


@router.get("/{snapshot_id}", response_model=NewsletterSnapshotRead)
def get_newsletter(
    snapshot_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> NewsletterSnapshot:
    snapshot = db.scalar(
        select(NewsletterSnapshot).where(
            NewsletterSnapshot.id == snapshot_id,
            NewsletterSnapshot.org_id == context.org_id,
        )
    )
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Newsletter not found")
    return snapshot

