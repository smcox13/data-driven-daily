from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.entities import DraftNewsletter, DraftStatus, NewsletterSnapshot
from app.services.rendering import render_html


def export_draft(session: Session, draft: DraftNewsletter) -> NewsletterSnapshot:
    preview_mjml, preview_html = render_html(draft.structure_json, draft.preview_mjml)
    html = draft.html_override or preview_html
    snapshot = NewsletterSnapshot(
        org_id=draft.org_id,
        draft_id=draft.id,
        issue_date=draft.issue_date,
        subject_line=draft.selected_subject_line or "Data-Driven Daily",
        html=html,
        mjml=preview_mjml,
        snapshot_json=draft.structure_json,
        export_metadata={"format": "mailchimp_html"},
    )
    draft.status = DraftStatus.EXPORTED.value
    draft.preview_html = html
    draft.preview_mjml = preview_mjml
    session.add(snapshot)
    session.flush()
    return snapshot

