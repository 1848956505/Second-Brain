from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from zoneinfo import ZoneInfo

from scripts.ai_daily.models import NewsItem


CATEGORY_ORDER = [
    "agent",
    "vibe_coding",
    "prompt_engineering",
    "github_projects",
    "model_news",
]

CATEGORY_NUMBER = {
    "agent": "01",
    "vibe_coding": "02",
    "prompt_engineering": "03",
    "github_projects": "04",
    "model_news": "05",
}


def _empty_report_content(day_str: str) -> str:
    return f"""# AI 技术情报日报｜{day_str}

> 今日未采集到满足质量阈值的内容。

## 今日重点

今日暂无高价值内容。

## 01 Agent 进展

今日暂无高价值内容。

## 02 Vibe Coding

今日暂无高价值内容。

## 03 Prompt Engineering

今日暂无高价值内容。

## 04 GitHub 热门 AI / Skills 项目

今日暂无高价值内容。

## 05 AI 大模型与多模态新闻

今日暂无高价值内容。
"""


def _render_non_github_item(item: NewsItem) -> str:
    return (
        f"### {item.title}\n\n"
        f"- 来源：{item.source}\n"
        f"- 链接：{item.url}\n"
        f"- 摘要：{item.summary}\n"
        f"- 推荐理由：{item.recommended_reason}\n"
        f"- 建议归档：`{item.suggested_archive}`\n"
        f"- 阅读优先级：{item.reading_priority}\n\n"
    )


def _render_github_table(items: List[NewsItem]) -> str:
    if not items:
        return "今日暂无高价值内容。\n\n"
    lines = [
        "| 项目 | 简介 | Stars | 最近更新 | 推荐理由 | 建议归档 |",
        "|---|---|---:|---|---|---|",
    ]
    for item in items:
        published = (item.published_at or "")[:10]
        lines.append(
            f"| [{item.repo_name or item.title}]({item.url}) | "
            f"{(item.summary or '').replace('|', '/')} | "
            f"{item.stars or 0} | "
            f"{published} | "
            f"{item.recommended_reason.replace('|', '/')} | "
            f"`{item.suggested_archive}` |"
        )
    return "\n".join(lines) + "\n\n"


def write_markdown_report(summarized: Dict[str, Any], config: Dict[str, Any]) -> str:
    report_cfg = config.get("report", {})
    tz_name = report_cfg.get("timezone", "Asia/Tokyo")
    now = datetime.now(ZoneInfo(tz_name))
    day_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M")

    items = summarized.get("items", [])
    output_dir = Path(report_cfg.get("output_dir", "00_Inbox/AI-Daily"))
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{day_str}.md"

    if not items:
        report_path.write_text(_empty_report_content(day_str), encoding="utf-8")
        return str(report_path)

    by_category: Dict[str, List[NewsItem]] = defaultdict(list)
    for item in items:
        by_category[item.category].append(item)

    today_keywords = summarized.get("today_keywords", [])[:3]
    highlights = summarized.get("top_highlights", [])[:3]
    categories_cfg = config.get("categories", {})

    lines = [
        f"# AI 技术情报日报｜{day_str}",
        "",
        f"> 自动采集时间：{time_str}",
        f"> 今日关键词：{' '.join([f'`{x}`' for x in today_keywords]) if today_keywords else '`暂无`'}",
        "> 说明：本日报为自动采集结果，正式知识笔记请学习后手动整理到对应分类文件夹。",
        "",
        "## 今日重点",
        "",
    ]

    if highlights:
        for i, h in enumerate(highlights, start=1):
            lines.append(f"{i}. **{h.get('title', '未命名')}**：{h.get('reason', '建议关注')}")
    else:
        lines.append("今日暂无高价值内容。")
    lines += ["", "---", ""]

    for category in CATEGORY_ORDER:
        title = categories_cfg.get(category, {}).get("title", category)
        section_num = CATEGORY_NUMBER[category]
        lines.append(f"## {section_num} {title}")
        lines.append("")

        category_items = by_category.get(category, [])
        if not category_items:
            lines.append("今日暂无高价值内容。")
            lines += ["", "---", ""]
            continue

        category_items = sorted(category_items, key=lambda x: x.final_score, reverse=True)
        if category == "github_projects":
            lines.append(_render_github_table(category_items).rstrip())
        else:
            for item in category_items:
                lines.append(_render_non_github_item(item).rstrip())
                lines.append("---")
                lines.append("")
        lines += ["---", ""]

    suggestions = summarized.get("collection_suggestions", {})
    lines += [
        "## 今日收藏建议",
        "",
        "### 值得精读",
        "",
    ]
    must_read = suggestions.get("must_read", [])
    lines.extend([f"- {x}" for x in must_read] or ["- 暂无"])
    lines += ["", "### 值得收藏", ""]
    worth_saving = suggestions.get("worth_saving", [])
    lines.extend([f"- {x}" for x in worth_saving] or ["- 暂无"])
    lines += ["", "### 可以略读", ""]
    can_skip = suggestions.get("can_skip", [])
    lines.extend([f"- {x}" for x in can_skip] or ["- 暂无"])
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)

