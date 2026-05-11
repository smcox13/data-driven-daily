from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DraftGenerateRequest(BaseModel):
    issue_date: date
    quick_hit_count: int = Field(default=5, ge=3, le=9)
    category_ids: list[str] = Field(default_factory=list)


class DraftSectionUpdate(BaseModel):
    title: str | None = None
    selected_subject_line: str | None = None
    preheader: str | None = None
    structure_json: dict[str, Any] | None = None


class HtmlOverrideRequest(BaseModel):
    html: str


class RegenerateRequest(BaseModel):
    section: str
    article_id: str | None = None


class DraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    issue_date: date
    status: str
    title: str
    selected_subject_line: str | None
    preheader: str | None
    structure_json: dict[str, Any]
    preview_html: str | None
    preview_mjml: str | None
    html_override: str | None
    generation_metadata: dict[str, Any]
    ai_provider: str
    model_map: dict[str, Any]
    created_at: datetime
    updated_at: datetime

