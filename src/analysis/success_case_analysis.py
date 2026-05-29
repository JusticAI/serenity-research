from __future__ import annotations

from src.domain.models import Post
from src.extraction.ticker_extractor import extract_tickers


def candidate_success_cases(posts: list[Post]) -> dict[str, list[str]]:
    cases: dict[str, list[str]] = {}
    for post in posts:
        for ticker in extract_tickers(post.text):
            cases.setdefault(ticker, []).append(post.text)
    return cases
