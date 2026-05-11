from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_context
from app.core.security import RequestContext
from app.models.entities import DraftNewsletter, NewsletterSnapshot
from app.schemas.newsletters import ExportResponse, NewsletterSnapshotRead
from app.services.exports import export_draft


router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/{draft_id}", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
def export_newsletter(
    draft_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ExportResponse:
    draft = db.scalar(
        select(DraftNewsletter).where(DraftNewsletter.id == draft_id, DraftNewsletter.org_id == context.org_id)
    )
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    snapshot = export_draft(db, draft)
    db.commit()
    db.refresh(snapshot)
    return ExportResponse(snapshot=NewsletterSnapshotRead.model_validate(snapshot), mailchimp_html=snapshot.html)


@router.get("/{draft_id}", response_model=NewsletterSnapshotRead)
def latest_export(
    draft_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> NewsletterSnapshot:
    snapshot = db.scalar(
        select(NewsletterSnapshot)
        .where(NewsletterSnapshot.draft_id == draft_id, NewsletterSnapshot.org_id == context.org_id)
        .order_by(NewsletterSnapshot.created_at.desc())
    )
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No export found for draft")
    return snapshot

