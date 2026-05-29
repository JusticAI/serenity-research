from __future__ import annotations

from src.domain.models import Post, Thesis, ThemeName
from src.extraction.ticker_extractor import extract_tickers
from src.extraction.theme_extractor import classify_text


def simple_thesis_from_post(post: Post) -> Thesis:
    themes = classify_text(post.text)
    top_theme = themes[0][0] if themes else ThemeName.UNKNOWN
    tickers = extract_tickers(post.text)
    text = post.text.strip()
    summary = text if len(text) <= 240 else text[:237] + "..."
    risks: list[str] = []
    lower = text.lower()
    if "delay" in lower or "risk" in lower or "struggle" in lower:
        risks.append("Execution or adoption risk mentioned in post")
    return Thesis(summary=summary, theme=top_theme, beneficiaries=tickers, risks=risks, confidence=0.45)
