from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import requests
from dateutil import parser

from scripts.ai_daily.models import NewsItem


GITHUB_SEARCH_API = "https://api.github.com/search/repositories"


def _build_headers() -> Dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _within_days(pushed_at: str | None, days: int) -> bool:
    if not pushed_at:
        return True
    try:
        dt = parser.parse(pushed_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt >= datetime.now(timezone.utc) - timedelta(days=days)
    except Exception:
        return True


def collect_github(config: Dict[str, Any]) -> List[NewsItem]:
    items: List[NewsItem] = []
    github_cfg = config.get("sources", {}).get("github", {})
    category_cfg = config.get("categories", {}).get("github_projects", {})
    queries = category_cfg.get("github_queries", [])
    per_query_limit = int(github_cfg.get("per_query_limit", 10))
    min_stars = int(github_cfg.get("min_stars", 20))
    pushed_within_days = int(github_cfg.get("pushed_within_days", 90))

    for query in queries:
        params = {
            "q": query,
            "sort": github_cfg.get("sort", "updated"),
            "order": github_cfg.get("order", "desc"),
            "per_page": per_query_limit,
        }
        try:
            response = requests.get(
                GITHUB_SEARCH_API,
                headers=_build_headers(),
                params=params,
                timeout=20,
            )
            if response.status_code >= 400:
                print(
                    f"[WARN] GitHub API failed for query '{query}': "
                    f"{response.status_code} {response.text[:200]}"
                )
                continue
            payload = response.json()
        except Exception as exc:
            print(f"[WARN] GitHub API request error for query '{query}': {exc}")
            continue

        for repo in payload.get("items", []):
            stars = repo.get("stargazers_count") or 0
            if stars < min_stars:
                continue
            if repo.get("archived"):
                continue
            if repo.get("fork"):
                continue
            if not _within_days(repo.get("pushed_at"), pushed_within_days):
                continue

            items.append(
                NewsItem(
                    id=repo.get("full_name", ""),
                    title=repo.get("full_name", ""),
                    url=repo.get("html_url", ""),
                    source="GitHub",
                    category="github_projects",
                    summary=repo.get("description") or "",
                    published_at=repo.get("pushed_at"),
                    stars=stars,
                    forks=repo.get("forks_count"),
                    language=repo.get("language"),
                    repo_name=repo.get("full_name"),
                    repo_description=repo.get("description"),
                    tags=repo.get("topics") or [],
                    raw=repo,
                )
            )
    return items

