from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from math import exp


@dataclass(slots=True)
class RankingCandidate:
    id: str
    publish_date: date | None
    source_authority_score: float
    ai_relevance_score: float
    editor_preference_score: float
    popularity_score: float = 0.0
    category_match_score: float = 0.5


def recency_score(publish_date: date | None, now: datetime | None = None) -> float:
    if publish_date is None:
        return 0.1
    current = now or datetime.now(UTC)
    age_days = max((current.date() - publish_date).days, 0)
    return float(exp(-age_days / 4))


def score_article(candidate: RankingCandidate, now: datetime | None = None) -> float:
    return round(
        (recency_score(candidate.publish_date, now) * 0.35)
        + (candidate.source_authority_score * 0.2)
        + (candidate.category_match_score * 0.15)
        + (candidate.editor_preference_score * 0.15)
        + (candidate.ai_relevance_score * 0.15),
        4,
    )

