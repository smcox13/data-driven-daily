from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AiProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    provider: str
    enabled: bool
    is_active: bool
    prompt_version: str
    api_base: str | None
    model_overrides: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class AiTaskConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_type: str
    model: str
    temperature: float
    max_tokens: int
    prompt_version: str
    extra_config: dict[str, Any]


class AiSettingsUpdate(BaseModel):
    active_provider: str
    prompt_version: str = "v1"
    model_overrides: dict[str, Any] = Field(default_factory=dict)
    task_models: dict[str, str] = Field(default_factory=dict)
