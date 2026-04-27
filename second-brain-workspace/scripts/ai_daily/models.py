from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NewsItem:
    id: str
    title: str
    url: str
    source: str
    category: str
    summary: str = ""
    author: Optional[str] = None
    published_at: Optional[str] = None
    collected_at: Optional[str] = None

    stars: Optional[int] = None
    forks: Optional[int] = None
    language: Optional[str] = None
    repo_name: Optional[str] = None
    repo_description: Optional[str] = None

    tags: List[str] = field(default_factory=list)
    raw: Dict = field(default_factory=dict)

    relevance_score: float = 0.0
    freshness_score: float = 0.0
    popularity_score: float = 0.0
    usefulness_score: float = 0.0
    final_score: float = 0.0

    recommended_reason: str = ""
    suggested_archive: str = ""
    reading_priority: str = "略读"

