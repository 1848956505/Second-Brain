from __future__ import annotations

import json
import os
import re
from collections import Counter
from typing import Any, Dict, List

import requests

from scripts.ai_daily.models import NewsItem


def _clean_text(text: str, max_len: int = 120) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]


def _priority_from_score(score: float) -> str:
    if score >= 88:
        return "精读"
    if score >= 80:
        return "收藏"
    return "略读"


def _fallback_reason(item: NewsItem) -> str:
    if item.category == "github_projects":
        return "项目活跃且有实用价值，适合加入工具库观察。"
    if item.category == "agent":
        return "与 Agent 实战能力相关，值得跟进其思路和实现。"
    if item.category == "vibe_coding":
        return "可直接改进 AI 编程工作流，具有较强实践价值。"
    if item.category == "prompt_engineering":
        return "对提示词设计与上下文组织有直接参考意义。"
    return "与大模型和多模态演进相关，建议保持关注。"


def _fallback_summarize(items: List[NewsItem], config: Dict[str, Any]) -> Dict[str, Any]:
    for item in items:
        item.summary = _clean_text(item.summary or item.repo_description or item.title, max_len=120)
        item.recommended_reason = item.recommended_reason or _fallback_reason(item)
        item.reading_priority = _priority_from_score(item.final_score)

    keywords = []
    for item in items:
        keywords.extend((item.tags or [])[:2])
        keywords.extend([k for k in re.findall(r"[A-Za-z][A-Za-z0-9\-\+\.]{2,}", item.title)][:2])
    today_keywords = [k for k, _ in Counter(keywords).most_common(3)] or ["Agent", "Workflow", "LLM"]

    top_items = sorted(items, key=lambda x: x.final_score, reverse=True)[:3]
    highlights = [{"title": it.title, "reason": it.recommended_reason} for it in top_items]

    return {
        "today_keywords": today_keywords,
        "top_highlights": highlights,
        "items_by_url": {
            it.url: {
                "summary": it.summary[:80],
                "recommended_reason": it.recommended_reason,
                "reading_priority": it.reading_priority,
            }
            for it in items
        },
        "collection_suggestions": {
            "must_read": [it.title for it in items if it.reading_priority == "精读"][:5],
            "worth_saving": [it.title for it in items if it.reading_priority == "收藏"][:8],
            "can_skip": [it.title for it in items if it.reading_priority == "略读"][:8],
        },
    }


def _llm_provider_config(provider: str) -> Dict[str, str] | None:
    provider = provider.lower()
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        return {"api_key": key or "", "base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"}
    if provider == "deepseek":
        key = os.getenv("DEEPSEEK_API_KEY")
        return {"api_key": key or "", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"}
    if provider == "qwen":
        key = os.getenv("QWEN_API_KEY")
        return {
            "api_key": key or "",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-plus",
        }
    return None


def _call_llm(items: List[NewsItem], config: Dict[str, Any]) -> Dict[str, Any] | None:
    llm_cfg = config.get("llm", {})
    if not llm_cfg.get("enabled", False):
        return None

    provider = os.getenv(llm_cfg.get("provider_env", "AI_DAILY_LLM_PROVIDER"), llm_cfg.get("default_provider", "none"))
    if provider == "none":
        return None

    provider_cfg = _llm_provider_config(provider)
    if not provider_cfg or not provider_cfg.get("api_key"):
        return None

    max_items = int(llm_cfg.get("max_input_items", 30))
    payload_items = []
    for item in sorted(items, key=lambda x: x.final_score, reverse=True)[:max_items]:
        payload_items.append(
            {
                "title": item.title,
                "url": item.url,
                "source": item.source,
                "category": item.category,
                "summary": _clean_text(item.summary, 180),
                "stars": item.stars,
                "published_at": item.published_at,
                "final_score": round(item.final_score, 2),
                "suggested_archive": item.suggested_archive,
            }
        )

    prompt = (
        "你是一个 AI 技术情报日报编辑。请根据给定的资料列表生成中文日报内容。\n\n"
        "要求：\n"
        "1. 只基于输入资料，不要编造事实。\n"
        "2. 每条摘要控制在 80 字以内。\n"
        "3. 推荐理由要说明为什么值得关注。\n"
        "4. 内容面向正在学习 AI Agent、Vibe Coding、Prompt Engineering、AI 项目的学生。\n"
        "5. 如果资料价值不高，可以标记为可略过。\n"
        "6. 输出结构必须是 JSON，不要输出 Markdown。\n"
    )
    body = {
        "model": provider_cfg["model"],
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(payload_items, ensure_ascii=False)},
        ],
        "temperature": 0.2,
    }
    try:
        resp = requests.post(
            f"{provider_cfg['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {provider_cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=45,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return {
            "today_keywords": parsed.get("today_keywords", []),
            "top_highlights": parsed.get("top_highlights", []),
            "items_by_url": {
                e.get("url"): {
                    "summary": e.get("summary", ""),
                    "recommended_reason": e.get("recommended_reason", ""),
                    "reading_priority": e.get("reading_priority", "略读"),
                }
                for e in parsed.get("items", [])
                if e.get("url")
            },
            "collection_suggestions": parsed.get("collection_suggestions", {}),
        }
    except Exception as exc:
        print(f"[WARN] LLM summarize failed, fallback to rules: {exc}")
        return None


def summarize_items(items: List[NewsItem], config: Dict[str, Any]) -> Dict[str, Any]:
    llm_output = _call_llm(items, config)
    if not llm_output:
        llm_output = _fallback_summarize(items, config)

    item_map = llm_output.get("items_by_url", {})
    for item in items:
        generated = item_map.get(item.url, {})
        if generated.get("summary"):
            item.summary = _clean_text(generated["summary"], 120)
        else:
            item.summary = _clean_text(item.summary, 120)

        item.recommended_reason = generated.get("recommended_reason") or item.recommended_reason or _fallback_reason(item)
        item.reading_priority = generated.get("reading_priority") or _priority_from_score(item.final_score)

    return {
        "today_keywords": llm_output.get("today_keywords", []),
        "top_highlights": llm_output.get("top_highlights", []),
        "collection_suggestions": llm_output.get("collection_suggestions", {}),
        "items": items,
    }

