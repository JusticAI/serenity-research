from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.domain.models import Post
from src.ingestion.normalize import normalize_row


def load_posts_from_csv(path: str | Path) -> list[Post]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    frame = pd.read_csv(csv_path).fillna("")
    posts: list[Post] = []
    seen: set[str] = set()
    for index, row in frame.iterrows():
        post = normalize_row(row.to_dict(), fallback_index=index)
        if post.external_id in seen:
            continue
        seen.add(post.external_id)
        posts.append(post)
    return posts
