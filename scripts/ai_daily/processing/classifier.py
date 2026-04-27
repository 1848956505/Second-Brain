from __future__ import annotations

from typing import Dict

DEFAULT_KEYWORDS: Dict[str, list[str]] = {
    "agent": [
        "agent",
        "智能体",
        "autonomous",
        "browser agent",
        "computer use",
        "mcp agent",
        "claude code",
        "codex",
        "openclaw",
        "harness",
    ],
    "vibe_coding": [
        "vibe coding",
        "cursor",
        "windsurf",
        "lovable",
        "bolt",
        "replit",
        "ai coding workflow",
        "ai 编程",
        "编程工作流",
        "教程",
        "tutorial",
        "workflow",
    ],
    "prompt_engineering": [
        "prompt",
        "提示词",
        "system prompt",
        "context engineering",
        "few-shot",
        "structured prompting",
    ],
    "github_projects": [
        "github",
        "repo",
        "repository",
        "mcp server",
        "skills",
        "open source",
    ],
    "model_news": [
        "openai",
        "claude",
        "gemini",
        "deepseek",
        "qwen",
        "kimi",
        "doubao",
        "llama",
        "multimodal",
        "多模态",
        "image generation",
        "video generation",
        "大模型",
    ],
}


def infer_category(text: str, default: str = "model_news") -> str:
    lowered = (text or "").lower()
    hits = {category: 0 for category in DEFAULT_KEYWORDS}
    for category, keywords in DEFAULT_KEYWORDS.items():
        for kw in keywords:
            if kw in lowered:
                hits[category] += 1

    if not any(hits.values()):
        return default

    if hits["vibe_coding"] and hits["agent"]:
        tutorial_like = any(k in lowered for k in ["教程", "tutorial", "workflow", "实战"])
        if tutorial_like:
            return "vibe_coding"
        return "agent"

    if hits["agent"] and ("claude code" in lowered or "codex" in lowered):
        tutorial_like = any(k in lowered for k in ["教程", "tutorial", "how to", "guide"])
        return "vibe_coding" if tutorial_like else "agent"

    return max(hits.items(), key=lambda x: x[1])[0]


def classify_item(item, config):
    if item.category == "github_projects":
        return item.category
    if item.source != "Bilibili" and item.category:
        return item.category
    content = f"{item.title}\n{item.summary}"
    item.category = infer_category(content, item.category or "model_news")
    return item.category


def classify_items(items, config):
    for item in items:
        classify_item(item, config)
    return items

