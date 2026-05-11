from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class NewsletterSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    draft_id: str
    issue_date: date
    subject_line: str
    html: str
    mjml: str | None
    snapshot_json: dict[str, Any]
    export_metadata: dict[str, Any]
    created_at: datetime


class ExportResponse(BaseModel):
    snapshot: NewsletterSnapshotRead
    mailchimp_html: str

