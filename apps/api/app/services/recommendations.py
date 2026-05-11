from __future__ import annotations

from collections import Counter
from typing import Iterable

from app.models.entities import Article, Source


def recommend_sources(selected_articles: Iterable[Article], sources: Iterable[Source], limit: int = 5) -> list[Source]:
    category_counts = Counter(article.category_id for article in selected_articles if article.category_id)
    ranked_sources = sorted(
        sources,
        key=lambda source: (
            category_counts.get(source.category_id, 0),
            source.authority_score,
            1 if source.enabled else 0,
        ),
        reverse=True,
    )
    return ranked_sources[:limit]


def suggest_replacements(current_article: Article, candidates: Iterable[Article], limit: int = 5) -> list[Article]:
    current_topic = (current_article.topic or "").lower()
    ranked = sorted(
        (
            article
            for article in candidates
            if article.id != current_article.id and not article.is_suppressed
        ),
        key=lambda article: (
            1 if current_topic and current_topic in (article.topic or "").lower() else 0,
            article.ranking_score,
        ),
        reverse=True,
    )
    return ranked[:limit]

