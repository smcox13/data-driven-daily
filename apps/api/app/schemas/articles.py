from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    url: str
    canonical_url: str
    author: str | None
    publish_date: date | None
    excerpt: str | None
    topic: str | None
    ranking_score: float
    popularity_score: float
    ai_relevance_score: float
    editor_preference_score: float
    source_authority_score: float
    is_suppressed: bool
    category_id: str | None
    created_at: datetime


class ArticleListResponse(BaseModel):
    items: list[ArticleRead]
    total: int


class IngestRequest(BaseModel):
    source_ids: list[str] | None = None
    refresh_ai_scores: bool = True


class ReplacementRequest(BaseModel):
    article_id: str
    replacement_article_id: str

