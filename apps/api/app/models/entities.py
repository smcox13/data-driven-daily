from __future__ import annotations

from datetime import UTC, datetime, date
from enum import StrEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(UTC)


def make_id() -> str:
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class UserRole(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"


class SourceType(StrEnum):
    RSS = "rss"
    MANUAL = "manual"


class BlockRuleType(StrEnum):
    DOMAIN = "domain"
    AUTHOR = "author"
    TOPIC = "topic"


class DraftStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    EXPORTED = "exported"


class FeedbackEventType(StrEnum):
    REMOVED = "removed"
    PROMOTED = "promoted"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    SUMMARY_EDITED = "summary_edited"
    REPLACED = "replaced"


class AiProvider(StrEnum):
    OPENAI = "openai"
    GEMINI = "gemini"


class AiTaskType(StrEnum):
    RELEVANCE = "relevance"
    SUMMARY = "summary"
    TLDR = "tldr"
    SUBJECT = "subject"
    REPLACEMENT = "replacement"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default=UserRole.EDITOR.value)
    google_sub: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="users")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(1024))
    type: Mapped[str] = mapped_column(String(32), default=SourceType.RSS.value)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    authority_score: Mapped[float] = mapped_column(Float, default=0.5)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class BlockRule(Base):
    __tablename__ = "block_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    type: Mapped[str] = mapped_column(String(32))
    value: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ArticleCluster(Base):
    __tablename__ = "article_clusters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    cluster_key: Mapped[str] = mapped_column(String(255), index=True)
    primary_article_id: Mapped[str | None] = mapped_column(ForeignKey("articles.id"), nullable=True)
    reason: Mapped[str] = mapped_column(String(255), default="similarity")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    source_id: Mapped[str | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    cluster_id: Mapped[str | None] = mapped_column(ForeignKey("article_clusters.id"), nullable=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(String(1024))
    canonical_url: Mapped[str] = mapped_column(String(1024), index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publish_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list)
    article_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    popularity_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_relevance_score: Mapped[float] = mapped_column(Float, default=0.5)
    editor_preference_score: Mapped[float] = mapped_column(Float, default=0.0)
    source_authority_score: Mapped[float] = mapped_column(Float, default=0.5)
    ranking_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_suppressed: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of_id: Mapped[str | None] = mapped_column(ForeignKey("articles.id"), nullable=True)
    embedding: Mapped[list[float]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class DraftNewsletter(Base):
    __tablename__ = "draft_newsletters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    issue_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default=DraftStatus.DRAFT.value)
    title: Mapped[str] = mapped_column(String(255), default="Data-Driven Daily")
    selected_subject_line: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preheader: Mapped[str | None] = mapped_column(String(255), nullable=True)
    structure_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    preview_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview_mjml: Mapped[str | None] = mapped_column(Text, nullable=True)
    html_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ai_provider: Mapped[str] = mapped_column(String(32), default=AiProvider.OPENAI.value)
    model_map: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class NewsletterSnapshot(Base):
    __tablename__ = "newsletter_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    draft_id: Mapped[str] = mapped_column(ForeignKey("draft_newsletters.id"), index=True)
    issue_date: Mapped[date] = mapped_column(Date)
    subject_line: Mapped[str] = mapped_column(String(255))
    html: Mapped[str] = mapped_column(Text)
    mjml: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    export_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    article_id: Mapped[str | None] = mapped_column(ForeignKey("articles.id"), nullable=True)
    draft_id: Mapped[str | None] = mapped_column(ForeignKey("draft_newsletters.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AiProviderConfig(Base):
    __tablename__ = "ai_provider_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    prompt_version: Mapped[str] = mapped_column(String(64), default="v1")
    api_base: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_overrides: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AiTaskConfig(Base):
    __tablename__ = "ai_task_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=make_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    provider_config_id: Mapped[str | None] = mapped_column(ForeignKey("ai_provider_configs.id"), nullable=True)
    task_type: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str] = mapped_column(String(255))
    temperature: Mapped[float] = mapped_column(Float, default=0.2)
    max_tokens: Mapped[int] = mapped_column(Integer, default=800)
    prompt_version: Mapped[str] = mapped_column(String(64), default="v1")
    extra_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

