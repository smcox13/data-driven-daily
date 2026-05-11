from __future__ import annotations

from app.core.config import get_settings

try:  # pragma: no cover - depends on optional local install
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - graceful fallback
    Celery = None


settings = get_settings()

celery_app = None
if Celery is not None:  # pragma: no cover - exercised only when Celery is installed
    celery_app = Celery("data_driven_daily", broker=settings.redis_url, backend=settings.redis_url)
    celery_app.conf.beat_schedule = {
        "ingest-feeds-every-30-minutes": {
            "task": "app.jobs.tasks.ingest_all_sources",
            "schedule": 1800.0,
        },
        "purge-articles-daily": {
            "task": "app.jobs.tasks.purge_old_articles",
            "schedule": 86400.0,
        },
    }

