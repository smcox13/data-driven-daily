from __future__ import annotations

import json

from openai import OpenAI

from app.core.config import Settings
from app.models.entities import Article
from app.services.ai.base import AiTaskResult
from app.services.ai.prompts import (
    RELEVANCE_PROMPT,
    REPLACEMENT_PROMPT,
    SUBJECT_PROMPT,
    SUMMARY_PROMPT,
    TLDR_PROMPT,
)


class OpenAIProvider:
    provider_name = "openai"

    def __init__(self, settings: Settings, model_map: dict[str, str] | None = None) -> None:
        self.settings = settings
        self.model_map = model_map or {}
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def _model(self, task: str) -> str:
        defaults = {
            "summary": self.settings.openai_summary_model,
            "relevance": self.settings.openai_ranking_model,
            "subject": self.settings.openai_subject_model,
            "tldr": self.settings.openai_default_model,
            "replacement": self.settings.openai_default_model,
        }
        return self.model_map.get(task, defaults[task])

    def _mock_result(self, task: str, article: Article | None = None, summaries: list[str] | None = None) -> AiTaskResult:
        if task == "summary" and article:
            excerpt = article.excerpt or article.text_content or article.title
            content = f"{article.title}: {excerpt[:220].strip()} This matters because it changes how marketing and data teams prioritize execution."
        elif task == "relevance" and article:
            keywords = article.topic or "marketing intelligence"
            content = json.dumps({"score": 0.74, "reason": f"Matches the newsletter focus on {keywords}."})
        elif task == "subject":
            highlights = summaries or ["AI, analytics, and martech shifts"]
            content = "\n".join(
                [
                    f"Data-Driven Daily: {highlights[0][:48]}",
                    "What marketing leaders need to know today",
                    "The analytics and AI moves shaping strategy this week",
                ]
            )
        elif task == "tldr":
            content = "Today’s issue tracks the highest-signal shifts across AI, analytics, privacy, and martech with clear executive takeaways."
        else:
            content = json.dumps({"article_id": article.id if article else "", "reason": "Closest topical fit."})
        return AiTaskResult(content=content, usage={"mode": "mock"}, model=f"mock-{task}")

    def _complete(self, task: str, system_prompt: str, user_prompt: str) -> AiTaskResult:
        if self.client is None:
            return AiTaskResult(content=user_prompt, usage={"mode": "no_api_key"}, model=self._model(task))
        response = self.client.responses.create(
            model=self._model(task),
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        text = response.output_text
        usage = {
            "input_tokens": getattr(response.usage, "input_tokens", 0),
            "output_tokens": getattr(response.usage, "output_tokens", 0),
            "total_tokens": getattr(response.usage, "total_tokens", 0),
        }
        return AiTaskResult(content=text, usage=usage, model=self._model(task))

    def score_relevance(self, article: Article, categories: list[str]) -> AiTaskResult:
        if self.client is None:
            return self._mock_result("relevance", article=article)
        prompt = (
            f"Categories: {', '.join(categories)}\n"
            f"Title: {article.title}\nExcerpt: {article.excerpt or ''}\nContent: {(article.text_content or '')[:2500]}"
        )
        return self._complete("relevance", RELEVANCE_PROMPT, prompt)

    def summarize_article(self, article: Article) -> AiTaskResult:
        if self.client is None:
            return self._mock_result("summary", article=article)
        prompt = f"Title: {article.title}\nExcerpt: {article.excerpt or ''}\nContent: {(article.text_content or '')[:4000]}"
        return self._complete("summary", SUMMARY_PROMPT, prompt)

    def generate_tldr(self, summaries: list[str]) -> AiTaskResult:
        if self.client is None:
            return self._mock_result("tldr")
        return self._complete("tldr", TLDR_PROMPT, "\n\n".join(summaries))

    def generate_subject_lines(self, summaries: list[str]) -> AiTaskResult:
        if self.client is None:
            return self._mock_result("subject", summaries=summaries)
        return self._complete("subject", SUBJECT_PROMPT, "\n\n".join(summaries))

    def suggest_replacements(self, prompt: str, candidates: list[Article]) -> AiTaskResult:
        if self.client is None:
            return self._mock_result("replacement", article=candidates[0] if candidates else None)
        candidate_lines = "\n".join([f"{article.id}: {article.title}" for article in candidates[:10]])
        return self._complete("replacement", REPLACEMENT_PROMPT, f"{prompt}\nCandidates:\n{candidate_lines}")

