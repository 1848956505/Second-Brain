from __future__ import annotations

import json
import re
import string
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List

from scripts.ai_daily.models import NewsItem


DECORATIVE_BRACKETS = re.compile(r"[【\[].*?[】\]]|\(.*?\)")
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAD6"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA70-\U0001FAFF"
    "]+",
    flags=re.UNICODE,
)


def normalize_title(title: str) -> str:
    text = (title or "").lower()
    text = DECORATIVE_BRACKETS.sub(" ", text)
    text = EMOJI_PATTERN.sub("", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", "", text)
    return text.strip()


def load_seen(path: str) -> Dict[str, Any]:
    seen_path = Path(path)
    if not seen_path.exists():
        seen = {"seen_urls": {}, "seen_titles": {}}
        seen_path.parent.mkdir(parents=True, exist_ok=True)
        seen_path.write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")
        return seen
    try:
        with seen_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("seen_urls", {})
        data.setdefault("seen_titles", {})
        return data
    except Exception:
        return {"seen_urls": {}, "seen_titles": {}}


def prune_seen(seen: Dict[str, Any], keep_days: int = 180) -> Dict[str, Any]:
    threshold = datetime.utcnow().date() - timedelta(days=keep_days)
    for key in ["seen_urls", "seen_titles"]:
        current = seen.get(key, {})
        kept = {}
        for value_key, meta in current.items():
            first_seen = (meta or {}).get("first_seen")
            if not first_seen:
                continue
            try:
                d = datetime.strptime(first_seen, "%Y-%m-%d").date()
            except Exception:
                continue
            if d >= threshold:
                kept[value_key] = meta
        seen[key] = kept
    return seen


def save_seen(seen: Dict[str, Any], path: str) -> None:
    seen = prune_seen(seen, keep_days=180)
    Path(path).write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")


def dedupe_items(items: List[NewsItem], seen: Dict[str, Any]) -> List[NewsItem]:
    seen_urls = set((seen.get("seen_urls") or {}).keys())
    seen_titles = set((seen.get("seen_titles") or {}).keys())

    deduped: List[NewsItem] = []
    for item in items:
        if not item.url:
            continue
        if item.url in seen_urls:
            continue

        normalized_title = normalize_title(item.title)
        if normalized_title and normalized_title in seen_titles:
            continue

        if item.repo_name:
            duplicated_repo = any(existing.repo_name == item.repo_name for existing in deduped if existing.repo_name)
            if duplicated_repo:
                continue

        replaced = False
        for idx, existing in enumerate(deduped):
            if not normalized_title:
                break
            existing_normalized = normalize_title(existing.title)
            if not existing_normalized:
                continue
            similarity = SequenceMatcher(None, normalized_title, existing_normalized).ratio()
            if similarity >= 0.92:
                current_score = item.final_score
                existing_score = existing.final_score
                if current_score > existing_score:
                    deduped[idx] = item
                replaced = True
                break
        if replaced:
            continue

        deduped.append(item)

    return deduped


def update_seen(seen: Dict[str, Any], items: List[NewsItem], day_str: str) -> None:
    seen_urls = seen.setdefault("seen_urls", {})
    seen_titles = seen.setdefault("seen_titles", {})
    for item in items:
        if item.url:
            seen_urls[item.url] = {
                "first_seen": day_str,
                "title": item.title,
            }
        normalized = normalize_title(item.title)
        if normalized:
            seen_titles[normalized] = {
                "first_seen": day_str,
                "url": item.url,
            }

