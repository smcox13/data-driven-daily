from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.entities import AiProvider, AiProviderConfig, AiTaskConfig
from app.services.ai.openai_provider import OpenAIProvider


class AiRegistry:
    def __init__(self, settings: Settings, session: Session, org_id: str) -> None:
        self.settings = settings
        self.session = session
        self.org_id = org_id

    def get_active_provider_config(self) -> AiProviderConfig | None:
        return self.session.scalar(
            select(AiProviderConfig).where(
                AiProviderConfig.org_id == self.org_id,
                AiProviderConfig.is_active.is_(True),
            )
        )

    def get_task_model_map(self, provider_config_id: str | None) -> dict[str, str]:
        if provider_config_id is None:
            return {}
        task_configs = self.session.scalars(
            select(AiTaskConfig).where(AiTaskConfig.provider_config_id == provider_config_id)
        ).all()
        return {task.task_type: task.model for task in task_configs}

    def get_provider(self):
        provider_config = self.get_active_provider_config()
        provider_name = provider_config.provider if provider_config else self.settings.default_ai_provider
        model_map = self.get_task_model_map(provider_config.id if provider_config else None)

        if provider_name == AiProvider.GEMINI.value:
            raise NotImplementedError("Gemini is configured but not implemented yet.")
        return OpenAIProvider(self.settings, model_map=model_map)

