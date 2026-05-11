from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from app.models.entities import FeedbackEvent, FeedbackEventType


EVENT_WEIGHTS = {
    FeedbackEventType.REMOVED.value: -0.5,
    FeedbackEventType.PROMOTED.value: 0.5,
    FeedbackEventType.THUMBS_UP.value: 0.35,
    FeedbackEventType.THUMBS_DOWN.value: -0.35,
    FeedbackEventType.SUMMARY_EDITED.value: 0.15,
    FeedbackEventType.REPLACED.value: -0.2,
}


def aggregate_editor_preferences(events: Iterable[FeedbackEvent]) -> dict[str, float]:
    scores: dict[str, float] = defaultdict(float)
    for event in events:
        if not event.article_id:
            continue
        scores[event.article_id] += EVENT_WEIGHTS.get(event.event_type, 0.0)
    return dict(scores)

