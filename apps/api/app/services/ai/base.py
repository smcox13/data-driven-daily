from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.models.entities import AiTaskType, Article


@dataclass(slots=True)
class AiTaskResult:
    content: str
    usage: dict[str, int | float | str]
    model: str


class AiProviderClient(Protocol):
    provider_name: str

    def score_relevance(self, article: Article, categories: list[str]) -> AiTaskResult:
        ...

    def summarize_article(self, article: Article) -> AiTaskResult:
        ...

    def generate_tldr(self, summaries: list[str]) -> AiTaskResult:
        ...

    def generate_subject_lines(self, summaries: list[str]) -> AiTaskResult:
        ...

    def suggest_replacements(self, prompt: str, candidates: list[Article]) -> AiTaskResult:
        ...


TASK_TO_CONFIG = {
    AiTaskType.RELEVANCE.value: "relevance",
    AiTaskType.SUMMARY.value: "summary",
    AiTaskType.TLDR.value: "tldr",
    AiTaskType.SUBJECT.value: "subject",
    AiTaskType.REPLACEMENT.value: "replacement",
}

