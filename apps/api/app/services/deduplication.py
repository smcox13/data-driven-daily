from __future__ import annotations

import re
from collections.abc import Iterable

from app.models.entities import Article


WORD_RE = re.compile(r"\w+")


def normalize_title(title: str) -> set[str]:
    return {word.lower() for word in WORD_RE.findall(title) if len(word) > 2}


def title_similarity(left: str, right: str) -> float:
    left_words = normalize_title(left)
    right_words = normalize_title(right)
    if not left_words or not right_words:
        return 0.0
    overlap = left_words & right_words
    union = left_words | right_words
    return len(overlap) / len(union)


def suppress_duplicates(articles: Iterable[Article], threshold: float = 0.65) -> list[Article]:
    primaries: list[Article] = []
    seen_canonical: dict[str, Article] = {}

    for article in sorted(articles, key=lambda item: item.source_authority_score, reverse=True):
        canonical = article.canonical_url or article.url
        if canonical in seen_canonical:
            article.is_suppressed = True
            article.duplicate_of_id = seen_canonical[canonical].id
            continue
        similar_primary = next(
            (primary for primary in primaries if title_similarity(primary.title, article.title) >= threshold),
            None,
        )
        if similar_primary:
            article.is_suppressed = True
            article.duplicate_of_id = similar_primary.id
            continue
        seen_canonical[canonical] = article
        article.is_suppressed = False
        primaries.append(article)
    return list(articles)

