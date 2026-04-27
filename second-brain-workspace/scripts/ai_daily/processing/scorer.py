from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from dateutil import parser

from scripts.ai_daily.models import NewsItem


def _get_category_keywords(config: Dict[str, Any], category: str) -> List[str]:
    return config.get("categories", {}).get(category, {}).get("keywords", []) or []


def _contains_any(text: str, keywords: List[str]) -> int:
    lowered = text.lower()
    return sum(1 for k in keywords if k.lower() in lowered)


def relevance_score(item: NewsItem, config: Dict[str, Any]) -> float:
    keywords = _get_category_keywords(config, item.category)
    title_hits = _contains_any(item.title, keywords)
    summary_hits = _contains_any(item.summary, keywords)
    tags_hits = _contains_any(" ".join(item.tags), keywords)

    score = 0
    if title_hits:
        score += 40
    if summary_hits:
        score += 25
    if tags_hits:
        score += 15
    if (title_hits + summary_hits + tags_hits) >= 2:
        score += 10
    return min(score, 100)


def freshness_score(item: NewsItem) -> float:
    if not item.published_at:
        return 50
    try:
        dt = parser.parse(item.published_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        days = delta.total_seconds() / 86400
    except Exception:
        return 50

    if days <= 1:
        return 100
    if days <= 2:
        return 90
    if days <= 3:
        return 80
    if days <= 7:
        return 65
    if days <= 30:
        return 40
    return 20


def popularity_score(item: NewsItem) -> float:
    if item.source == "GitHub":
        stars = int(item.stars or 0)
        if stars >= 10000:
            return 100
        if stars >= 3000:
            return 90
        if stars >= 1000:
            return 80
        if stars >= 300:
            return 65
        if stars >= 100:
            return 50
        if stars >= 20:
            return 35
        return 20
    return 50


def usefulness_score(item: NewsItem) -> float:
    text = f"{item.title} {item.summary}".lower()
    score = 10

    if re.search(r"(教程|guide|tutorial|workflow|best practices|模板|实战|demo)", text):
        score += 30
    if re.search(r"(开源|github|repo|mcp server|framework)", text):
        score += 25
    if re.search(r"(release|benchmark|发布)", text):
        score += 20
    if re.search(r"(营销|带货|训练营|速成课|副业变现)", text):
        score -= 30

    if item.source == "GitHub" and not (item.repo_description or "").strip():
        score -= 10

    return max(min(score, 100), 0)


def score_items(items: List[NewsItem], config: Dict[str, Any]) -> List[NewsItem]:
    for item in items:
        item.relevance_score = relevance_score(item, config)
        item.freshness_score = freshness_score(item)
        item.popularity_score = popularity_score(item)
        item.usefulness_score = usefulness_score(item)
        item.final_score = (
            item.relevance_score * 0.40
            + item.freshness_score * 0.25
            + item.popularity_score * 0.20
            + item.usefulness_score * 0.15
        )
    return items

