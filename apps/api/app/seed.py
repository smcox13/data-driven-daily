from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.entities import AiProvider, AiProviderConfig, AiTaskConfig, AiTaskType, Article, Category, Organization, Source, SourceType, User, UserRole
from app.services.ranking import RankingCandidate, score_article


def slugify(text: str) -> str:
    return text.lower().replace("&", "and").replace(" ", "-")


def seed_demo_content(session: Session, organization: Organization) -> None:
    existing_articles = session.scalars(select(Article).where(Article.org_id == organization.id)).first()
    if existing_articles is not None:
        return

    categories = {
        category.slug: category
        for category in session.scalars(select(Category).where(Category.org_id == organization.id)).all()
    }

    sources = session.scalars(select(Source).where(Source.org_id == organization.id)).all()
    source_by_name = {source.name: source for source in sources}

    demo_source_specs = [
        {
            "name": "MarTech",
            "url": "https://example.com/demo/martech",
            "authority_score": 0.86,
            "category_slug": "marketing-technology",
            "notes": "Demo source for local editorial workflow testing."
        },
        {
            "name": "Data Strategy Journal",
            "url": "https://example.com/demo/data-strategy",
            "authority_score": 0.79,
            "category_slug": "business-intelligence",
            "notes": "Demo source for measurement and analytics coverage."
        },
    ]

    for spec in demo_source_specs:
        if spec["name"] in source_by_name:
            continue
        source = Source(
            org_id=organization.id,
            category_id=categories[spec["category_slug"]].id if spec["category_slug"] in categories else None,
            name=spec["name"],
            url=spec["url"],
            type=SourceType.MANUAL.value,
            enabled=True,
            authority_score=spec["authority_score"],
            notes=spec["notes"],
        )
        session.add(source)
        session.flush()
        source_by_name[source.name] = source

    today = date.today()
    demo_articles = [
        {
            "title": "Retail media budgets shift toward first-party measurement stacks",
            "url": "https://example.com/demo/article-1",
            "author": "Jordan Lee",
            "publish_date": today,
            "excerpt": "Brands are reallocating budget toward measurement layers that unify retail media, CRM, and incrementality reporting.",
            "topic": "retail media measurement budget",
            "category_slug": "crm-and-customer-data",
            "source_name": "Data Strategy Journal",
            "ai_relevance_score": 0.89,
            "editor_preference_score": 0.21,
        },
        {
            "title": "Privacy rule changes force martech vendors to rework identity workflows",
            "url": "https://example.com/demo/article-2",
            "author": "Avery Patel",
            "publish_date": today,
            "excerpt": "Identity orchestration vendors are adapting consent flows and enrichment pipelines to stay compliant.",
            "topic": "privacy consent identity workflows",
            "category_slug": "data-privacy",
            "source_name": "MarTech",
            "ai_relevance_score": 0.87,
            "editor_preference_score": 0.19,
        },
        {
            "title": "AI copilots are moving from dashboard summaries into campaign operations",
            "url": "https://example.com/demo/article-3",
            "author": "Samir Chen",
            "publish_date": today - timedelta(days=1),
            "excerpt": "Teams are pushing AI assistants closer to briefing, segmentation, and optimization workflows.",
            "topic": "ai copilots campaign operations",
            "category_slug": "ai-and-machine-learning",
            "source_name": "MarTech",
            "ai_relevance_score": 0.83,
            "editor_preference_score": 0.11,
        },
        {
            "title": "Email teams are redesigning lifecycle programs around zero-party data",
            "url": "https://example.com/demo/article-4",
            "author": "Morgan Ruiz",
            "publish_date": today - timedelta(days=1),
            "excerpt": "Lifecycle marketers are reworking segmentation and creative decisioning around explicit customer-provided signals.",
            "topic": "email lifecycle zero party data",
            "category_slug": "email-marketing",
            "source_name": "MarTech",
            "ai_relevance_score": 0.8,
            "editor_preference_score": 0.12,
        },
        {
            "title": "Marketing analytics leaders are consolidating BI layers to speed decision cycles",
            "url": "https://example.com/demo/article-5",
            "author": "Nina Brooks",
            "publish_date": today - timedelta(days=2),
            "excerpt": "Teams are simplifying reporting stacks to reduce dashboard sprawl and improve executive alignment.",
            "topic": "marketing analytics business intelligence",
            "category_slug": "business-intelligence",
            "source_name": "Data Strategy Journal",
            "ai_relevance_score": 0.78,
            "editor_preference_score": 0.09,
        },
    ]

    for spec in demo_articles:
        source = source_by_name[spec["source_name"]]
        article = Article(
            org_id=organization.id,
            source_id=source.id,
            category_id=categories[spec["category_slug"]].id if spec["category_slug"] in categories else None,
            title=spec["title"],
            url=spec["url"],
            canonical_url=spec["url"],
            author=spec["author"],
            publish_date=spec["publish_date"],
            excerpt=spec["excerpt"],
            text_content=spec["excerpt"],
            topic=spec["topic"],
            keywords=spec["topic"].split(),
            article_metadata={"seeded": True},
            popularity_score=0.0,
            ai_relevance_score=spec["ai_relevance_score"],
            editor_preference_score=spec["editor_preference_score"],
            source_authority_score=source.authority_score,
            is_suppressed=False,
        )
        article.ranking_score = score_article(
            RankingCandidate(
                id=article.id,
                publish_date=article.publish_date,
                source_authority_score=article.source_authority_score,
                ai_relevance_score=article.ai_relevance_score,
                editor_preference_score=article.editor_preference_score,
                category_match_score=0.8,
            )
        )
        session.add(article)


def seed_defaults(session: Session, settings: Settings) -> None:
    organization = session.scalar(select(Organization).where(Organization.slug == settings.default_org_slug))
    if organization is None:
        organization = Organization(name=settings.default_org_name, slug=settings.default_org_slug)
        session.add(organization)
        session.flush()

    admin_user = session.scalar(select(User).where(User.email == "editor@datadrivendaily.local"))
    if admin_user is None:
        admin_user = User(
            org_id=organization.id,
            email="editor@datadrivendaily.local",
            name="Demo Editor",
            role=UserRole.ADMIN.value,
        )
        session.add(admin_user)

    existing_categories = {
        category.name for category in session.scalars(select(Category).where(Category.org_id == organization.id)).all()
    }
    for category_name in settings.initial_categories:
        if category_name not in existing_categories:
            session.add(Category(org_id=organization.id, name=category_name, slug=slugify(category_name)))

    provider = session.scalar(
        select(AiProviderConfig).where(
            AiProviderConfig.org_id == organization.id,
            AiProviderConfig.provider == AiProvider.OPENAI.value,
        )
    )
    if provider is None:
        provider = AiProviderConfig(
            org_id=organization.id,
            provider=AiProvider.OPENAI.value,
            enabled=True,
            is_active=True,
            prompt_version="v1",
            model_overrides={
                AiTaskType.SUMMARY.value: settings.openai_summary_model,
                AiTaskType.RELEVANCE.value: settings.openai_ranking_model,
                AiTaskType.SUBJECT.value: settings.openai_subject_model,
                AiTaskType.TLDR.value: settings.openai_default_model,
                AiTaskType.REPLACEMENT.value: settings.openai_default_model,
            },
        )
        session.add(provider)
        session.flush()

    gemini_provider = session.scalar(
        select(AiProviderConfig).where(
            AiProviderConfig.org_id == organization.id,
            AiProviderConfig.provider == AiProvider.GEMINI.value,
        )
    )
    if gemini_provider is None:
        session.add(
            AiProviderConfig(
                org_id=organization.id,
                provider=AiProvider.GEMINI.value,
                enabled=False,
                is_active=False,
                prompt_version="v1",
                model_overrides={},
            )
        )

    existing_task_types = {
        task.task_type for task in session.scalars(select(AiTaskConfig).where(AiTaskConfig.org_id == organization.id)).all()
    }
    for task_type, model in provider.model_overrides.items():
        if task_type in existing_task_types:
            continue
        session.add(
            AiTaskConfig(
                org_id=organization.id,
                provider_config_id=provider.id,
                task_type=task_type,
                model=model,
                temperature=0.2,
                max_tokens=900,
                prompt_version="v1",
            )
        )

    if settings.allow_demo_auth:
        seed_demo_content(session, organization)
