from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: str) -> Dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def ensure_dirs(config: Dict[str, Any]) -> None:
    report = config.get("report", {})
    output_dir = Path(report.get("output_dir", "00_Inbox/AI-Daily"))
    seen_file = Path(report.get("seen_file", "data/ai_daily_seen.json"))

    output_dir.mkdir(parents=True, exist_ok=True)
    seen_file.parent.mkdir(parents=True, exist_ok=True)

    if not seen_file.exists():
        seen_file.write_text(
            json.dumps({"seen_urls": {}, "seen_titles": {}}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

