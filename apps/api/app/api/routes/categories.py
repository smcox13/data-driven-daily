from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_context
from app.core.security import RequestContext
from app.models.entities import Category
from app.schemas.sources import CategoryCreate, CategoryRead


router = APIRouter(prefix="/categories", tags=["categories"])


def slugify(text: str) -> str:
    return text.lower().replace("&", "and").replace(" ", "-")


@router.get("", response_model=list[CategoryRead])
def list_categories(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[Category]:
    return db.scalars(select(Category).where(Category.org_id == context.org_id).order_by(Category.name.asc())).all()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Category:
    existing = db.scalar(
        select(Category).where(Category.org_id == context.org_id, Category.slug == slugify(payload.name))
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    category = Category(org_id=context.org_id, name=payload.name, slug=slugify(payload.name))
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

