from __future__ import annotations

import json
from pathlib import Path

from src.domain.models import Post
from src.ingestion.normalize import normalize_row


def load_posts_from_json(path: str | Path) -> list[Post]:
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON not found: {json_path}")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("posts", [])
    posts: list[Post] = []
    seen: set[str] = set()
    for index, row in enumerate(data):
        post = normalize_row(row, fallback_index=index)
        if post.external_id in seen:
            continue
        seen.add(post.external_id)
        posts.append(post)
    return posts
