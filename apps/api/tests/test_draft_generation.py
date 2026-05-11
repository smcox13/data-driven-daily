from __future__ import annotations

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.models.entities import AiProviderConfig, Article, Base, Category, Organization, User
from app.services.drafts import generate_draft


def test_generate_draft_builds_structured_issue() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    settings = Settings(
        database_url="sqlite+pysqlite:///:memory:",
        openai_api_key=None,
        allow_demo_auth=True,
    )

    with session_factory() as session:
        org = Organization(name="Demo Org", slug="demo-org")
        session.add(org)
        session.flush()
        user = User(org_id=org.id, email="editor@example.com", name="Editor", role="admin")
        category = Category(org_id=org.id, name="AI & Machine Learning", slug="ai-machine-learning")
        session.add_all([user, category])
        session.flush()
        session.add(
            AiProviderConfig(
                org_id=org.id,
                provider="openai",
                enabled=True,
                is_active=True,
                prompt_version="v1",
                model_overrides={},
            )
        )
        session.add_all(
            [
                Article(
                    org_id=org.id,
                    category_id=category.id,
                    title="Featured story",
                    url="https://example.com/1",
                    canonical_url="https://example.com/1",
                    excerpt="A featured article about strategy.",
                    publish_date=date(2026, 5, 11),
                    source_authority_score=0.9,
                    ranking_score=0.95,
                ),
                Article(
                    org_id=org.id,
                    category_id=category.id,
                    title="Quick hit one",
                    url="https://example.com/2",
                    canonical_url="https://example.com/2",
                    excerpt="A second article about execution.",
                    publish_date=date(2026, 5, 11),
                    source_authority_score=0.8,
                    ranking_score=0.85,
                ),
                Article(
                    org_id=org.id,
                    category_id=category.id,
                    title="Quick hit two",
                    url="https://example.com/3",
                    canonical_url="https://example.com/3",
                    excerpt="A third article about measurement.",
                    publish_date=date(2026, 5, 11),
                    source_authority_score=0.78,
                    ranking_score=0.83,
                ),
                Article(
                    org_id=org.id,
                    category_id=category.id,
                    title="Quick hit three",
                    url="https://example.com/4",
                    canonical_url="https://example.com/4",
                    excerpt="A fourth article about privacy.",
                    publish_date=date(2026, 5, 11),
                    source_authority_score=0.77,
                    ranking_score=0.82,
                ),
            ]
        )
        session.commit()

        draft = generate_draft(
            session=session,
            org_id=org.id,
            user_id=user.id,
            issue_date=date(2026, 5, 11),
            quick_hit_count=3,
            category_ids=[],
            settings=settings,
        )

        assert draft.structure_json["featured_insight"]["title"] == "Featured story"
        assert len(draft.structure_json["quick_hits"]) == 3
        assert draft.selected_subject_line
        assert draft.preview_html

