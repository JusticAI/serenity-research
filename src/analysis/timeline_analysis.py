from __future__ import annotations

from collections import defaultdict

from src.domain.models import Post


def posts_by_year(posts: list[Post]) -> dict[str, list[Post]]:
    grouped: dict[str, list[Post]] = defaultdict(list)
    for post in posts:
        year = str(post.created_at.year) if post.created_at else "unknown"
        grouped[year].append(post)
    return dict(sorted(grouped.items()))
