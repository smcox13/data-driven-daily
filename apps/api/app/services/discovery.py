from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Article, BlockRule, BlockRuleType, Source


@dataclass(slots=True)
class FeedEntry:
    title: str
    url: str
    author: str | None
    published: date | None
    excerpt: str | None


def slugify_topic(title: str) -> str:
    words = [word.lower() for word in title.split() if len(word) > 3]
    return " ".join(words[:4])


def parse_rss_feed(feed_url: str) -> list[FeedEntry]:
    response = requests.get(feed_url, timeout=10)
    response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    items = root.findall(".//item") or root.findall(".//entry")
    entries: list[FeedEntry] = []
    for item in items:
        title = item.findtext("title") or "Untitled"
        link = item.findtext("link")
        if link is None:
            link_el = item.find("link")
            link = link_el.get("href") if link_el is not None else None
        if not link:
            continue
        pub_date = item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}updated")
        published = parsedate_to_datetime(pub_date).date() if pub_date else None
        description = item.findtext("description") or item.findtext("summary")
        author = item.findtext("author")
        entries.append(
            FeedEntry(
                title=unescape(title.strip()),
                url=link.strip(),
                author=author.strip() if author else None,
                published=published,
                excerpt=BeautifulSoup(description or "", "html.parser").get_text(" ", strip=True),
            )
        )
    return entries


def extract_article_text(url: str) -> tuple[str | None, str]:
    response = requests.get(url, timeout=10, headers={"User-Agent": "DataDrivenDailyBot/1.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    canonical = soup.find("link", rel="canonical")
    canonical_url = canonical.get("href") if canonical and canonical.get("href") else url
    paragraphs = [node.get_text(" ", strip=True) for node in soup.find_all("p")]
    text_content = "\n".join([paragraph for paragraph in paragraphs if paragraph])
    return text_content or None, canonical_url


def find_blocked_values(session: Session, org_id: str) -> dict[str, set[str]]:
    rules = session.scalars(select(BlockRule).where(BlockRule.org_id == org_id)).all()
    blocked: dict[str, set[str]] = {
        BlockRuleType.DOMAIN.value: set(),
        BlockRuleType.AUTHOR.value: set(),
        BlockRuleType.TOPIC.value: set(),
    }
    for rule in rules:
        blocked.setdefault(rule.type, set()).add(rule.value.lower())
    return blocked


def is_blocked(entry: FeedEntry, blocked: dict[str, set[str]]) -> bool:
    domain = urlparse(entry.url).netloc.lower()
    topic = slugify_topic(entry.title)
    return (
        domain in blocked.get(BlockRuleType.DOMAIN.value, set())
        or (entry.author or "").lower() in blocked.get(BlockRuleType.AUTHOR.value, set())
        or topic in blocked.get(BlockRuleType.TOPIC.value, set())
    )


def ingest_source(session: Session, org_id: str, source: Source) -> list[Article]:
    blocked = find_blocked_values(session, org_id)
    discovered_articles: list[Article] = []
    for entry in parse_rss_feed(source.url):
        if is_blocked(entry, blocked):
            continue
        article = Article(
            org_id=org_id,
            source_id=source.id,
            category_id=source.category_id,
            title=entry.title,
            url=entry.url,
            canonical_url=entry.url,
            author=entry.author,
            publish_date=entry.published,
            excerpt=entry.excerpt,
            topic=slugify_topic(entry.title),
            source_authority_score=source.authority_score,
            article_metadata={"discovered_at": datetime.utcnow().isoformat()},
        )
        try:
            text_content, canonical_url = extract_article_text(entry.url)
            article.text_content = text_content
            article.canonical_url = canonical_url
        except requests.RequestException:
            article.text_content = entry.excerpt
        discovered_articles.append(article)
    return discovered_articles

