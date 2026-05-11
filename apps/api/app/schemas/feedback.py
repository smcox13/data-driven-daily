from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    article_id: str | None = None
    draft_id: str | None = None
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)

