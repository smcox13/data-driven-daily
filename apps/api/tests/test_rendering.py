from __future__ import annotations

from app.services.rendering import render_html


def test_render_html_returns_mjml_and_html() -> None:
    payload = {
        "issue_date": "2026-05-11",
        "featured_insight": {
            "title": "Featured insight",
            "url": "https://example.com",
            "summary": "Important executive summary."
        },
        "quick_hits": [],
        "tldr": "Short summary.",
        "cta": {"headline": "Data Corner", "body": "Use the signal."},
        "footer": {"brand": "Data-Driven Daily", "disclaimer": "Review before send."}
    }

    mjml, html = render_html(payload)

    assert "<mjml>" in mjml
    assert "<html" in html.lower()
    assert "Featured insight" in html

