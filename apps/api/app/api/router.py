from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import ai, articles, categories, drafts, exports, feedback, newsletters, sources


api_router = APIRouter(prefix="/api")
api_router.include_router(sources.router)
api_router.include_router(categories.router)
api_router.include_router(articles.router)
api_router.include_router(drafts.router)
api_router.include_router(newsletters.router)
api_router.include_router(feedback.router)
api_router.include_router(ai.router)
api_router.include_router(exports.router)

