from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.jobs.celery_app import celery_app
from app.models.entities import Article, Organization, Source
from app.seed import seed_defaults
from app.services.deduplication import suppress_duplicates
from app.services.discovery import ingest_source
from app.services.drafts import sync_article_preference_scores
from app.services.ranking import RankingCandidate, score_article


def _refresh_rankings(articles: list[Article]) -> None:
    for article in articles:
        article.ranking_score = score_article(
            RankingCandidate(
                id=article.id,
                publish_date=article.publish_date,
                source_authority_score=article.source_authority_score,
                ai_relevance_score=article.ai_relevance_score,
                editor_preference_score=article.editor_preference_score,
                category_match_score=0.75 if article.category_id else 0.5,
            )
        )


def _ingest_all_sources() -> int:
    settings = get_settings()
    with SessionLocal() as session:
        seed_defaults(session, settings)
        session.commit()
        organizations = session.scalars(select(Organization)).all()
        created = 0
        for organization in organizations:
            sources = session.scalars(
                select(Source).where(Source.org_id == organization.id, Source.enabled.is_(True))
            ).all()
            for source in sources:
                for article in ingest_source(session, organization.id, source):
                    existing = session.scalar(
                        select(Article).where(
                            Article.org_id == organization.id,
                            Article.canonical_url == article.canonical_url,
                        )
                    )
                    if existing:
                        continue
                    session.add(article)
                    created += 1
            all_articles = session.scalars(select(Article).where(Article.org_id == organization.id)).all()
            sync_article_preference_scores(session, organization.id)
            suppress_duplicates(all_articles)
            _refresh_rankings(all_articles)
        session.commit()
        return created


def _purge_old_articles() -> int:
    cutoff = datetime.now(UTC).date() - timedelta(days=30)
    with SessionLocal() as session:
        result = session.execute(delete(Article).where(Article.publish_date < cutoff))
        session.commit()
        return result.rowcount or 0


if celery_app is not None:  # pragma: no cover - depends on Celery install
    @celery_app.task(name="app.jobs.tasks.ingest_all_sources")
    def ingest_all_sources() -> int:
        return _ingest_all_sources()

    @celery_app.task(name="app.jobs.tasks.purge_old_articles")
    def purge_old_articles() -> int:
        return _purge_old_articles()

