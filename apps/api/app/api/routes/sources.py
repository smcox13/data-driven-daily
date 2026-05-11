from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_context
from app.core.security import RequestContext
from app.models.entities import BlockRule, Source
from app.schemas.common import MessageResponse
from app.schemas.sources import BlockRulePayload, SourceCreate, SourceRead, SourceUpdate


router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceRead])
def list_sources(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[Source]:
    return db.scalars(select(Source).where(Source.org_id == context.org_id).order_by(Source.created_at.desc())).all()


@router.get("/block-rules", response_model=list[BlockRulePayload])
def list_block_rules(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[BlockRule]:
    return db.scalars(select(BlockRule).where(BlockRule.org_id == context.org_id)).all()


@router.post("/block-rules", response_model=BlockRulePayload, status_code=status.HTTP_201_CREATED)
def create_block_rule(
    payload: BlockRulePayload,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> BlockRule:
    rule = BlockRule(org_id=context.org_id, **payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(
    payload: SourceCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Source:
    source = Source(org_id=context.org_id, **payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.patch("/{source_id}", response_model=SourceRead)
def update_source(
    source_id: str,
    payload: SourceUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Source:
    source = db.scalar(select(Source).where(Source.id == source_id, Source.org_id == context.org_id))
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(source, field, value)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}", response_model=MessageResponse)
def delete_source(
    source_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> MessageResponse:
    source = db.scalar(select(Source).where(Source.id == source_id, Source.org_id == context.org_id))
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    db.delete(source)
    db.commit()
    return MessageResponse(message="Source deleted")


@router.delete("/block-rules/{rule_type}/{value}", response_model=MessageResponse)
def delete_block_rule(
    rule_type: str,
    value: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> MessageResponse:
    db.execute(
        delete(BlockRule).where(
            BlockRule.org_id == context.org_id,
            BlockRule.type == rule_type,
            BlockRule.value == value,
        )
    )
    db.commit()
    return MessageResponse(message="Block rule deleted")
