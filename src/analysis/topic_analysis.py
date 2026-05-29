from __future__ import annotations

from collections import Counter

from src.domain.models import Post
from src.extraction.theme_extractor import classify_text
from src.extraction.ticker_extractor import extract_tickers


def theme_counts(posts: list[Post]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for post in posts:
        for theme, score in classify_text(post.text):
            counter[theme.value] += int(score)
    return counter


def ticker_counts(posts: list[Post]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for post in posts:
        counter.update(extract_tickers(post.text))
    return counter
