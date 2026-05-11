from __future__ import annotations

from app.models.entities import Article
from app.services.deduplication import suppress_duplicates, title_similarity


def make_article(article_id: str, title: str, canonical_url: str, authority: float) -> Article:
    return Article(
        id=article_id,
        org_id="org-1",
        title=title,
        url=canonical_url,
        canonical_url=canonical_url,
        source_authority_score=authority,
    )


def test_title_similarity_detects_close_variants() -> None:
    similarity = title_similarity(
        "Retail media budgets move toward first-party measurement",
        "First-party measurement is attracting more retail media budget",
    )
    assert similarity >= 0.45


def test_duplicate_articles_are_suppressed() -> None:
    primary = make_article("1", "Privacy rules reshape martech identity workflows", "https://example.com/1", 0.9)
    duplicate = make_article("2", "Privacy rules reshape identity workflows in martech", "https://example.com/2", 0.5)
    unique = make_article("3", "AI copilots enter campaign operations", "https://example.com/3", 0.7)

    suppress_duplicates([primary, duplicate, unique], threshold=0.45)

    assert primary.is_suppressed is False
    assert duplicate.is_suppressed is True
    assert duplicate.duplicate_of_id == primary.id
    assert unique.is_suppressed is False

