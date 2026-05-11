from __future__ import annotations

from datetime import UTC, date, datetime

from app.services.ranking import RankingCandidate, recency_score, score_article


def test_recency_score_drops_with_age() -> None:
    today = datetime(2026, 5, 11, tzinfo=UTC)
    newer = recency_score(date(2026, 5, 11), now=today)
    older = recency_score(date(2026, 5, 1), now=today)

    assert newer > older
    assert 0 < older < 1


def test_score_article_favors_stronger_signals() -> None:
    now = datetime(2026, 5, 11, tzinfo=UTC)
    strong = RankingCandidate(
        id="strong",
        publish_date=date(2026, 5, 11),
        source_authority_score=0.9,
        ai_relevance_score=0.85,
        editor_preference_score=0.4,
        category_match_score=0.8,
    )
    weak = RankingCandidate(
        id="weak",
        publish_date=date(2026, 4, 20),
        source_authority_score=0.4,
        ai_relevance_score=0.3,
        editor_preference_score=-0.2,
        category_match_score=0.4,
    )

    assert score_article(strong, now=now) > score_article(weak, now=now)

