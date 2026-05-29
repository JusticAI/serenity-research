from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from src.domain.models import Post

COLUMN_ALIASES = {
    "tweet_id": ["tweet_id", "id", "external_id", "status_id"],
    "created_at": ["created_at", "date", "time", "timestamp"],
    "author": ["author", "username", "handle", "user"],
    "text": ["text", "content", "body", "full_text", "tweet"],
    "url": ["url", "link", "tweet_url"],
    "like_count": ["like_count", "likes", "favorite_count", "favorites"],
    "repost_count": ["repost_count", "retweets", "retweet_count", "reposts"],
    "reply_count": ["reply_count", "replies"],
    "quote_count": ["quote_count", "quotes"],
}


def _first_present(row: dict[str, Any], aliases: list[str], default: Any = None) -> Any:
    for alias in aliases:
        if alias in row and row[alias] not in (None, ""):
            return row[alias]
    return default


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text


def parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    raw = str(value).strip()
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_int(value: Any) -> int:
    if value in (None, ""):
        return 0
    try:
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return 0


def normalize_row(row: dict[str, Any], fallback_index: int) -> Post:
    text = clean_text(_first_present(row, COLUMN_ALIASES["text"], ""))
    if not text:
        raise ValueError("Row has no text/content field")

    external_id = str(_first_present(row, COLUMN_ALIASES["tweet_id"], f"row-{fallback_index}"))
    return Post(
        external_id=external_id,
        created_at=parse_datetime(_first_present(row, COLUMN_ALIASES["created_at"])),
        author=str(_first_present(row, COLUMN_ALIASES["author"], "unknown")),
        text=text,
        url=_first_present(row, COLUMN_ALIASES["url"]),
        likes=parse_int(_first_present(row, COLUMN_ALIASES["like_count"])),
        reposts=parse_int(_first_present(row, COLUMN_ALIASES["repost_count"])),
        replies=parse_int(_first_present(row, COLUMN_ALIASES["reply_count"])),
        quotes=parse_int(_first_present(row, COLUMN_ALIASES["quote_count"])),
    )
