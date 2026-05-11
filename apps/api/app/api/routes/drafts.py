from __future__ import annotations

import copy

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_context, get_settings_dep
from app.core.config import Settings
from app.core.security import RequestContext
from app.models.entities import Article, DraftNewsletter
from app.schemas.articles import ReplacementRequest
from app.schemas.common import MessageResponse
from app.schemas.drafts import DraftGenerateRequest, DraftRead, DraftSectionUpdate, HtmlOverrideRequest, RegenerateRequest
from app.services.ai.registry import AiRegistry
from app.services.drafts import available_replacements, generate_draft, refresh_draft_preview, source_recommendations


router = APIRouter(prefix="/drafts", tags=["drafts"])


def get_draft_or_404(db: Session, org_id: str, draft_id: str) -> DraftNewsletter:
    draft = db.scalar(select(DraftNewsletter).where(DraftNewsletter.id == draft_id, DraftNewsletter.org_id == org_id))
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return draft


@router.get("", response_model=list[DraftRead])
def list_drafts(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[DraftNewsletter]:
    return db.scalars(
        select(DraftNewsletter).where(DraftNewsletter.org_id == context.org_id).order_by(DraftNewsletter.created_at.desc())
    ).all()


@router.post("/generate", response_model=DraftRead, status_code=status.HTTP_201_CREATED)
def create_draft(
    payload: DraftGenerateRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> DraftNewsletter:
    draft = generate_draft(
        session=db,
        org_id=context.org_id,
        user_id=context.user_id,
        issue_date=payload.issue_date,
        quick_hit_count=payload.quick_hit_count,
        category_ids=payload.category_ids,
        settings=settings,
    )
    db.commit()
    db.refresh(draft)
    return draft


@router.get("/{draft_id}", response_model=DraftRead)
def get_draft(
    draft_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DraftNewsletter:
    return get_draft_or_404(db, context.org_id, draft_id)


@router.patch("/{draft_id}", response_model=DraftRead)
def update_draft(
    draft_id: str,
    payload: DraftSectionUpdate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DraftNewsletter:
    draft = get_draft_or_404(db, context.org_id, draft_id)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(draft, field, value)
    refresh_draft_preview(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.post("/{draft_id}/replace", response_model=DraftRead)
def replace_article(
    draft_id: str,
    payload: ReplacementRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DraftNewsletter:
    draft = get_draft_or_404(db, context.org_id, draft_id)
    current = db.scalar(select(Article).where(Article.id == payload.article_id, Article.org_id == context.org_id))
    replacement = db.scalar(
        select(Article).where(Article.id == payload.replacement_article_id, Article.org_id == context.org_id)
    )
    if current is None or replacement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    from app.services.drafts import replace_draft_article

    replace_draft_article(draft, current, replacement, db)
    db.commit()
    db.refresh(draft)
    return draft


@router.get("/{draft_id}/replacements/{article_id}", response_model=list[dict])
def get_replacements(
    draft_id: str,
    article_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _draft = get_draft_or_404(db, context.org_id, draft_id)
    article = db.scalar(select(Article).where(Article.id == article_id, Article.org_id == context.org_id))
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return [
        {"id": candidate.id, "title": candidate.title, "url": candidate.url, "score": candidate.ranking_score}
        for candidate in available_replacements(db, context.org_id, article)
    ]


@router.post("/{draft_id}/regenerate", response_model=DraftRead)
def regenerate_draft_content(
    draft_id: str,
    payload: RegenerateRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> DraftNewsletter:
    draft = get_draft_or_404(db, context.org_id, draft_id)
    registry = AiRegistry(settings, db, context.org_id)
    provider = registry.get_provider()
    structure = copy.deepcopy(draft.structure_json)

    if payload.section == "tldr":
        summaries = [structure["featured_insight"]["summary"], *[item["summary"] for item in structure["quick_hits"]]]
        structure["tldr"] = provider.generate_tldr(summaries).content
    elif payload.section == "subject_lines":
        summaries = [structure["featured_insight"]["summary"], *[item["summary"] for item in structure["quick_hits"]]]
        structure["subject_lines"] = [
            line.strip("- ").strip()
            for line in provider.generate_subject_lines(summaries).content.splitlines()
            if line.strip()
        ]
        draft.selected_subject_line = structure["subject_lines"][0] if structure["subject_lines"] else draft.selected_subject_line
    elif payload.article_id:
        article = db.scalar(select(Article).where(Article.id == payload.article_id, Article.org_id == context.org_id))
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        summary = provider.summarize_article(article).content
        if structure["featured_insight"]["article_id"] == article.id:
            structure["featured_insight"]["summary"] = summary
        for item in structure["quick_hits"]:
            if item["article_id"] == article.id:
                item["summary"] = summary
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid regenerate request")

    draft.structure_json = structure
    refresh_draft_preview(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.post("/{draft_id}/html-override", response_model=DraftRead)
def save_html_override(
    draft_id: str,
    payload: HtmlOverrideRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DraftNewsletter:
    draft = get_draft_or_404(db, context.org_id, draft_id)
    draft.html_override = payload.html
    draft.preview_html = payload.html
    db.commit()
    db.refresh(draft)
    return draft


@router.delete("/{draft_id}/html-override", response_model=DraftRead)
def discard_html_override(
    draft_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> DraftNewsletter:
    draft = get_draft_or_404(db, context.org_id, draft_id)
    draft.html_override = None
    refresh_draft_preview(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.get("/{draft_id}/source-recommendations", response_model=list[dict])
def get_source_recommendations(
    draft_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    draft = get_draft_or_404(db, context.org_id, draft_id)
    return [
        {"id": source.id, "name": source.name, "url": source.url, "authority_score": source.authority_score}
        for source in source_recommendations(db, context.org_id, draft)
    ]

