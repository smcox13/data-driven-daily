from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Data-Driven Daily API"
    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./data_driven_daily.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_shared_secret: str = "change-me"
    allow_demo_auth: bool = True

    default_org_name: str = "Data-Driven Daily"
    default_org_slug: str = "data-driven-daily"

    default_ai_provider: str = "openai"
    openai_api_key: str | None = None
    openai_default_model: str = "gpt-4.1-mini"
    openai_summary_model: str = "gpt-4.1"
    openai_ranking_model: str = "gpt-4.1-mini"
    openai_subject_model: str = "gpt-4.1-mini"

    initial_categories: list[str] = Field(
        default_factory=lambda: [
            "AI & Machine Learning",
            "Marketing Technology",
            "Data Privacy",
            "Email Marketing",
            "Direct Mail",
            "Business Intelligence",
            "CRM & Customer Data",
            "Retail Analytics",
        ]
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

