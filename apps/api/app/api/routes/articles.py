from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_context, get_settings_dep
from app.core.config import Settings
from app.core.security import RequestContext
from app.models.entities import Article, Source
from app.schemas.articles import ArticleListResponse, IngestRequest
from app.services.deduplication import suppress_duplicates
from app.services.discovery import ingest_source
from app.services.drafts import sync_article_preference_scores
from app.services.ranking import RankingCandidate, score_article


router = APIRouter(prefix="/articles", tags=["articles"])


def refresh_rankings(articles: list[Article]) -> None:
    for article in articles:
        candidate = RankingCandidate(
            id=article.id,
            publish_date=article.publish_date,
            source_authority_score=article.source_authority_score,
            ai_relevance_score=article.ai_relevance_score,
            editor_preference_score=article.editor_preference_score,
            popularity_score=article.popularity_score,
            category_match_score=0.75 if article.category_id else 0.5,
        )
        article.ranking_score = score_article(candidate)


@router.get("", response_model=ArticleListResponse)
def list_articles(
    keyword: str | None = None,
    source_id: str | None = None,
    category_id: str | None = None,
    author: str | None = None,
    include_suppressed: bool = False,
    published_after: date | None = None,
    limit: int = Query(default=25, le=100),
    offset: int = 0,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ArticleListResponse:
    query = select(Article).where(Article.org_id == context.org_id)
    total_query = select(func.count()).select_from(Article).where(Article.org_id == context.org_id)

    if keyword:
        predicate = or_(Article.title.ilike(f"%{keyword}%"), Article.excerpt.ilike(f"%{keyword}%"))
        query = query.where(predicate)
        total_query = total_query.where(predicate)
    if source_id:
        query = query.where(Article.source_id == source_id)
        total_query = total_query.where(Article.source_id == source_id)
    if category_id:
        query = query.where(Article.category_id == category_id)
        total_query = total_query.where(Article.category_id == category_id)
    if author:
        query = query.where(Article.author.ilike(f"%{author}%"))
        total_query = total_query.where(Article.author.ilike(f"%{author}%"))
    if published_after:
        query = query.where(Article.publish_date >= published_after)
        total_query = total_query.where(Article.publish_date >= published_after)
    if not include_suppressed:
        query = query.where(Article.is_suppressed.is_(False))
        total_query = total_query.where(Article.is_suppressed.is_(False))

    items = db.scalars(query.order_by(Article.ranking_score.desc(), Article.publish_date.desc()).offset(offset).limit(limit)).all()
    total = db.scalar(total_query) or 0
    return ArticleListResponse(items=items, total=total)


@router.post("/ingest", response_model=ArticleListResponse)
def ingest_articles(
    payload: IngestRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> ArticleListResponse:
    source_query = select(Source).where(Source.org_id == context.org_id, Source.enabled.is_(True))
    if payload.source_ids:
        source_query = source_query.where(Source.id.in_(payload.source_ids))
    sources = db.scalars(source_query).all()

    ingested: list[Article] = []
    for source in sources:
        for article in ingest_source(db, context.org_id, source):
            existing = db.scalar(
                select(Article).where(
                    Article.org_id == context.org_id,
                    Article.canonical_url == article.canonical_url,
                )
            )
            if existing:
                continue
            db.add(article)
            ingested.append(article)

    db.flush()
    sync_article_preference_scores(db, context.org_id)
    all_articles = db.scalars(select(Article).where(Article.org_id == context.org_id)).all()
    suppress_duplicates(all_articles)
    refresh_rankings(all_articles)
    db.commit()

    recent = db.scalars(
        select(Article).where(Article.org_id == context.org_id).order_by(Article.created_at.desc()).limit(50)
    ).all()
    return ArticleListResponse(items=recent, total=len(recent))

