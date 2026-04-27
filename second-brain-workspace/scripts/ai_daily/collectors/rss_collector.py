from __future__ import annotations

from typing import Any, Dict, List

import feedparser

from scripts.ai_daily.models import NewsItem


def collect_rss(config: Dict[str, Any], seen: Dict[str, Any]) -> List[NewsItem]:
    items: List[NewsItem] = []
    feeds = config.get("sources", {}).get("rss", {}).get("feeds", [])
    seen_urls = seen.get("seen_urls", {})

    for feed in feeds:
        feed_name = feed.get("name", "RSS")
        feed_category = feed.get("category", "model_news")
        feed_url = feed.get("url")
        if not feed_url:
            continue

        try:
            parsed = feedparser.parse(feed_url)
            if getattr(parsed, "bozo", False):
                print(f"[WARN] RSS parse warning: {feed_name}")
        except Exception as exc:
            print(f"[WARN] RSS parse failed for '{feed_name}': {exc}")
            continue

        for entry in parsed.entries:
            link = (entry.get("link") or "").strip()
            title = (entry.get("title") or "").strip()
            summary = (entry.get("summary") or entry.get("description") or "").strip()
            if not link:
                continue
            if link in seen_urls:
                continue
            if not title and not summary:
                continue
            items.append(
                NewsItem(
                    id=link,
                    title=title or "Untitled",
                    url=link,
                    source=feed_name,
                    category=feed_category,
                    summary=summary,
                    published_at=entry.get("published") or entry.get("updated"),
                    raw=dict(entry),
                )
            )

    return items

