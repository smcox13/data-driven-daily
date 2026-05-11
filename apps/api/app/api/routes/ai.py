from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_context
from app.core.security import RequestContext
from app.models.entities import AiProviderConfig, AiTaskConfig
from app.schemas.ai import AiProviderRead, AiSettingsUpdate, AiTaskConfigRead


router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/providers", response_model=list[AiProviderRead])
def list_providers(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[AiProviderConfig]:
    return db.scalars(
        select(AiProviderConfig).where(AiProviderConfig.org_id == context.org_id).order_by(AiProviderConfig.provider.asc())
    ).all()


@router.get("/settings", response_model=dict)
def get_ai_settings(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    providers = db.scalars(select(AiProviderConfig).where(AiProviderConfig.org_id == context.org_id)).all()
    tasks = db.scalars(select(AiTaskConfig).where(AiTaskConfig.org_id == context.org_id)).all()
    active = next((provider.provider for provider in providers if provider.is_active), None)
    return {
        "active_provider": active,
        "providers": [AiProviderRead.model_validate(provider).model_dump() for provider in providers],
        "task_configs": [AiTaskConfigRead.model_validate(task).model_dump() for task in tasks],
    }


@router.patch("/settings", response_model=dict)
def update_ai_settings(
    payload: AiSettingsUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    providers = db.scalars(select(AiProviderConfig).where(AiProviderConfig.org_id == context.org_id)).all()
    target_provider = next((provider for provider in providers if provider.provider == payload.active_provider), None)
    if target_provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    for provider in providers:
        provider.is_active = provider.id == target_provider.id
        if provider.id == target_provider.id:
            provider.prompt_version = payload.prompt_version
            provider.model_overrides = payload.model_overrides

    task_configs = db.scalars(select(AiTaskConfig).where(AiTaskConfig.org_id == context.org_id)).all()
    for task in task_configs:
        if task.task_type in payload.task_models:
            task.model = payload.task_models[task.task_type]

    db.commit()
    return get_ai_settings(context=context, db=db)

