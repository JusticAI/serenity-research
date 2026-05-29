from __future__ import annotations

import re

from src.domain.models import Post, TickerMention

TICKER_PATTERN = re.compile(r"(?<![A-Z0-9])\$([A-Z]{1,5})(?![A-Z0-9])")


def extract_tickers(text: str) -> list[str]:
    return sorted(set(match.group(1).upper() for match in TICKER_PATTERN.finditer(text)))


def extract_ticker_mentions(posts: list[Post]) -> list[TickerMention]:
    mentions: list[TickerMention] = []
    for post in posts:
        for ticker in extract_tickers(post.text):
            mentions.append(TickerMention(ticker=ticker, post_external_id=post.external_id))
    return mentions
