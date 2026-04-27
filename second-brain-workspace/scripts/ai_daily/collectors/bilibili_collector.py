from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List
from urllib.parse import quote

import feedparser
import requests

from scripts.ai_daily.models import NewsItem
from scripts.ai_daily.processing.classifier import infer_category


def _route_category_by_keyword(keyword: str) -> str:
    kw = keyword.lower()
    if any(x in kw for x in ["prompt", "提示词", "context"]):
        return "prompt_engineering"
    if any(x in kw for x in ["vibe", "cursor", "windsurf", "lovable", "bolt", "编程"]):
        return "vibe_coding"
    if any(x in kw for x in ["agent", "智能体", "mcp", "claude code", "codex"]):
        return "agent"
    if any(x in kw for x in ["model", "大模型", "多模态", "deepseek", "qwen"]):
        return "model_news"
    return "model_news"


def collect_bilibili(config: Dict[str, Any]) -> List[NewsItem]:
    items: List[NewsItem] = []
    bilibili_cfg = config.get("sources", {}).get("bilibili", {})
    base_url = bilibili_cfg.get("rsshub_base_url", "https://rsshub.app").rstrip("/")
    keywords = bilibili_cfg.get("keywords", [])
    orders = bilibili_cfg.get("orders", ["pubdate", "stow"])
    per_keyword_limit = int(bilibili_cfg.get("per_keyword_limit", 5))

    per_keyword_count = defaultdict(int)
    seen_links = set()

    for keyword in keywords:
        seed_category = _route_category_by_keyword(keyword)
        for order in orders:
            encoded = quote(keyword)
            url = f"{base_url}/bilibili/vsearch/{encoded}/{order}"
            try:
                response = requests.get(url, timeout=20)
                response.raise_for_status()
                parsed = feedparser.parse(response.text)
            except Exception as exc:
                print(f"[WARN] RSSHub Bilibili failed: kw='{keyword}', order='{order}', err={exc}")
                continue

            for entry in parsed.entries:
                link = (entry.get("link") or "").strip()
                if not link or link in seen_links:
                    continue
                if per_keyword_count[keyword] >= per_keyword_limit:
                    break

                title = (entry.get("title") or "").strip()
                summary = (entry.get("summary") or "").strip()
                combined = f"{title}\n{summary}\n{keyword}"
                category = infer_category(combined, seed_category)

                seen_links.add(link)
                per_keyword_count[keyword] += 1
                items.append(
                    NewsItem(
                        id=link,
                        title=title or "Untitled",
                        url=link,
                        source="Bilibili",
                        category=category,
                        summary=summary,
                        author=entry.get("author"),
                        published_at=entry.get("published") or entry.get("updated"),
                        raw=dict(entry),
                    )
                )

    return items

