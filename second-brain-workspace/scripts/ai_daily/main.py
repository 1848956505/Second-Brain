from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

from zoneinfo import ZoneInfo

from scripts.ai_daily.collectors.bilibili_collector import collect_bilibili
from scripts.ai_daily.collectors.github_collector import collect_github
from scripts.ai_daily.collectors.rss_collector import collect_rss
from scripts.ai_daily.config_loader import ensure_dirs, load_config
from scripts.ai_daily.models import NewsItem
from scripts.ai_daily.processing.classifier import classify_items
from scripts.ai_daily.processing.dedupe import dedupe_items, load_seen, save_seen, update_seen
from scripts.ai_daily.processing.scorer import score_items
from scripts.ai_daily.processing.summarizer import summarize_items
from scripts.ai_daily.report.markdown_writer import write_markdown_report


def _day_str(config: Dict[str, Any]) -> str:
    tz_name = config.get("report", {}).get("timezone", "Asia/Tokyo")
    return datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d")


def normalize_items(items: List[NewsItem], config: Dict[str, Any]) -> List[NewsItem]:
    categories = config.get("categories", {})
    for item in items:
        if not item.title:
            item.title = "Untitled"
        if not item.summary:
            item.summary = item.repo_description or ""
        item.suggested_archive = categories.get(item.category, {}).get("suggested_archive", "")
    return items


def select_items(items: List[NewsItem], limits: Dict[str, Any]) -> List[NewsItem]:
    min_score = float(limits.get("min_score", 75))
    total_max = int(limits.get("total_max", 15))
    per_category_max = int(limits.get("per_category_max", 3))

    candidates = [item for item in items if item.final_score >= min_score]
    grouped = defaultdict(list)
    for item in candidates:
        grouped[item.category].append(item)

    selected: List[NewsItem] = []
    for _, group in grouped.items():
        selected.extend(sorted(group, key=lambda x: x.final_score, reverse=True)[:per_category_max])

    selected = sorted(selected, key=lambda x: x.final_score, reverse=True)[:total_max]
    return selected


def fallback_expand_recent_items(all_items: List[NewsItem], selected: List[NewsItem], limits: Dict[str, Any]) -> List[NewsItem]:
    if len(selected) >= int(limits.get("fallback", {}).get("if_total_less_than", 5)):
        return selected

    total_max = int(limits.get("total_max", 15))
    min_score = float(limits.get("min_score", 75)) - 10
    selected_urls = {item.url for item in selected}

    fallback_items = [item for item in all_items if item.url not in selected_urls and item.final_score >= min_score]
    fallback_items = sorted(fallback_items, key=lambda x: x.final_score, reverse=True)
    combined = selected + fallback_items
    return combined[:total_max]


def main() -> None:
    config = load_config("config/ai_daily_sources.yaml")
    ensure_dirs(config)

    seen_path = config.get("report", {}).get("seen_file", "data/ai_daily_seen.json")
    seen = load_seen(seen_path)

    items: List[NewsItem] = []

    if config.get("sources", {}).get("github", {}).get("enabled", False):
        items.extend(collect_github(config))
    if config.get("sources", {}).get("rss", {}).get("enabled", False):
        items.extend(collect_rss(config, seen))
    if config.get("sources", {}).get("bilibili", {}).get("enabled", False):
        items.extend(collect_bilibili(config))

    items = normalize_items(items, config)
    items = classify_items(items, config)
    items = dedupe_items(items, seen)
    items = score_items(items, config)

    # Re-run dedupe after scoring so high-score duplicate survives.
    items = dedupe_items(sorted(items, key=lambda x: x.final_score, reverse=True), seen)

    limits = config.get("daily_limits", {})
    selected = select_items(items, limits)
    selected = fallback_expand_recent_items(items, selected, limits)
    selected = selected[: int(limits.get("total_max", 15))]

    summarized = summarize_items(selected, config)
    report_path = write_markdown_report(summarized, config)

    update_seen(seen, selected, _day_str(config))
    save_seen(seen, seen_path)

    print(f"Generated report: {report_path}")


if __name__ == "__main__":
    main()

