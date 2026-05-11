from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_context
from app.core.security import RequestContext
from app.models.entities import FeedbackEvent
from app.schemas.common import MessageResponse
from app.schemas.feedback import FeedbackCreate


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> MessageResponse:
    feedback = FeedbackEvent(
        org_id=context.org_id,
        user_id=context.user_id,
        article_id=payload.article_id,
        draft_id=payload.draft_id,
        event_type=payload.event_type,
        payload=payload.payload,
    )
    db.add(feedback)
    db.commit()
    return MessageResponse(message="Feedback recorded")

