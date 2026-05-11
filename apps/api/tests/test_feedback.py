from __future__ import annotations

from app.models.entities import FeedbackEvent
from app.services.feedback import aggregate_editor_preferences


def test_feedback_aggregation_combines_positive_and_negative_signals() -> None:
    events = [
      FeedbackEvent(id="1", org_id="org-1", article_id="article-1", event_type="thumbs_up"),
      FeedbackEvent(id="2", org_id="org-1", article_id="article-1", event_type="promoted"),
      FeedbackEvent(id="3", org_id="org-1", article_id="article-2", event_type="removed"),
    ]

    scores = aggregate_editor_preferences(events)

    assert scores["article-1"] > 0
    assert scores["article-2"] < 0

