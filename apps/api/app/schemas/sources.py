from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import SourceType


class BlockRulePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str


class SourceCreate(BaseModel):
    name: str
    url: str
    type: str = SourceType.RSS.value
    category_id: str | None = None
    authority_score: float = Field(default=0.5, ge=0.0, le=1.0)
    notes: str | None = None


class SourceUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    enabled: bool | None = None
    category_id: str | None = None
    authority_score: float | None = Field(default=None, ge=0.0, le=1.0)
    notes: str | None = None


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    url: str
    type: str
    enabled: bool
    category_id: str | None
    authority_score: float
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CategoryCreate(BaseModel):
    name: str


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
