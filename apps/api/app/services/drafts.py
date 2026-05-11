from __future__ import annotations

import json
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.entities import Article, DraftNewsletter, DraftStatus, FeedbackEvent, Source
from app.services.ai.registry import AiRegistry
from app.services.feedback import aggregate_editor_preferences
from app.services.recommendations import recommend_sources, suggest_replacements
from app.services.rendering import render_html


def build_subject_lines(raw_text: str) -> list[str]:
    return [line.strip("- ").strip() for line in raw_text.splitlines() if line.strip()]


def parse_relevance_score(raw: str) -> float:
    try:
        payload = json.loads(raw)
        return float(payload.get("score", 0.5))
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0.5


def build_newsletter_payload(
    featured_article: Article,
    quick_hits: list[Article],
    summaries: dict[str, str],
    tldr: str,
    subject_lines: list[str],
    issue_date: date,
) -> dict[str, Any]:
    featured = {
        "article_id": featured_article.id,
        "title": featured_article.title,
        "url": featured_article.url,
        "summary": summaries[featured_article.id],
    }
    quick_hit_items = [
        {
            "article_id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": summaries[article.id],
        }
        for article in quick_hits
    ]
    return {
        "issue_date": issue_date.isoformat(),
        "featured_insight": featured,
        "quick_hits": quick_hit_items,
        "tldr": tldr,
        "cta": {
            "headline": "Data Corner",
            "body": "Use today’s signals to sharpen media allocation, measurement, and customer data priorities."
        },
        "footer": {
            "brand": "Data-Driven Daily",
            "disclaimer": "Prepared for editorial review. Validate facts before distribution."
        },
        "subject_lines": subject_lines,
    }


def generate_draft(
    session: Session,
    org_id: str,
    user_id: str,
    issue_date: date,
    quick_hit_count: int,
    category_ids: list[str],
    settings: Settings,
) -> DraftNewsletter:
    ai_registry = AiRegistry(settings, session, org_id)
    provider = ai_registry.get_provider()

    articles = session.scalars(
        select(Article).where(
            Article.org_id == org_id,
            Article.is_suppressed.is_(False),
            Article.publish_date.is_not(None),
        ).order_by(Article.ranking_score.desc(), Article.publish_date.desc())
    ).all()

    if category_ids:
        articles = [article for article in articles if article.category_id in category_ids]
    if len(articles) < quick_hit_count + 1:
        raise ValueError("Not enough ranked articles available to build a draft.")

    featured = articles[0]
    quick_hits = articles[1 : quick_hit_count + 1]
    summaries: dict[str, str] = {}
    usage: dict[str, Any] = {"summaries": {}, "relevance": {}}

    for article in [featured, *quick_hits]:
        summary_result = provider.summarize_article(article)
        summaries[article.id] = summary_result.content.strip()
        usage["summaries"][article.id] = summary_result.usage
        relevance_result = provider.score_relevance(article, settings.initial_categories)
        article.ai_relevance_score = parse_relevance_score(relevance_result.content)
        usage["relevance"][article.id] = relevance_result.usage

    tldr_result = provider.generate_tldr(list(summaries.values()))
    subject_result = provider.generate_subject_lines(list(summaries.values()))
    subject_lines = build_subject_lines(subject_result.content)

    payload = build_newsletter_payload(featured, quick_hits, summaries, tldr_result.content, subject_lines, issue_date)
    preview_mjml, preview_html = render_html(payload)

    draft = DraftNewsletter(
        org_id=org_id,
        created_by=user_id,
        issue_date=issue_date,
        status=DraftStatus.DRAFT.value,
        title=f"Data-Driven Daily | {issue_date.isoformat()}",
        selected_subject_line=subject_lines[0] if subject_lines else None,
        preheader="Executive intelligence for data, AI, martech, and measurement leaders.",
        structure_json=payload,
        preview_html=preview_html,
        preview_mjml=preview_mjml,
        generation_metadata={
            "usage": {
                "tldr": tldr_result.usage,
                "subject": subject_result.usage,
                **usage,
            },
            "provider": provider.provider_name,
        },
        ai_provider=provider.provider_name,
        model_map={"default": getattr(provider, "_model", lambda _task: "unknown")("summary")},
    )
    session.add(draft)
    session.flush()
    return draft


def refresh_draft_preview(draft: DraftNewsletter) -> DraftNewsletter:
    preview_mjml, preview_html = render_html(draft.structure_json)
    draft.preview_mjml = preview_mjml
    draft.preview_html = draft.html_override or preview_html
    return draft


def replace_draft_article(
    draft: DraftNewsletter,
    current_article: Article,
    replacement: Article,
    session: Session,
) -> DraftNewsletter:
    structure = draft.structure_json
    if structure["featured_insight"]["article_id"] == current_article.id:
        structure["featured_insight"]["article_id"] = replacement.id
        structure["featured_insight"]["title"] = replacement.title
        structure["featured_insight"]["url"] = replacement.url
    for item in structure["quick_hits"]:
        if item["article_id"] == current_article.id:
            item["article_id"] = replacement.id
            item["title"] = replacement.title
            item["url"] = replacement.url
    draft.structure_json = structure
    refresh_draft_preview(draft)

    feedback = FeedbackEvent(
        org_id=draft.org_id,
        user_id=draft.created_by,
        article_id=current_article.id,
        draft_id=draft.id,
        event_type="replaced",
        payload={"replacement_article_id": replacement.id},
    )
    session.add(feedback)
    return draft


def available_replacements(session: Session, org_id: str, article: Article) -> list[Article]:
    candidates = session.scalars(
        select(Article).where(Article.org_id == org_id, Article.is_suppressed.is_(False)).order_by(Article.ranking_score.desc())
    ).all()
    return suggest_replacements(article, candidates)


def source_recommendations(session: Session, org_id: str, draft: DraftNewsletter) -> list[Source]:
    article_ids = [
        draft.structure_json["featured_insight"]["article_id"],
        *[item["article_id"] for item in draft.structure_json["quick_hits"]],
    ]
    articles = session.scalars(select(Article).where(Article.id.in_(article_ids))).all()
    sources = session.scalars(select(Source).where(Source.org_id == org_id)).all()
    return recommend_sources(articles, sources)


def sync_article_preference_scores(session: Session, org_id: str) -> None:
    events = session.scalars(select(FeedbackEvent).where(FeedbackEvent.org_id == org_id)).all()
    scores = aggregate_editor_preferences(events)
    if not scores:
        return
    articles = session.scalars(select(Article).where(Article.org_id == org_id)).all()
    for article in articles:
        article.editor_preference_score = scores.get(article.id, 0.0)

