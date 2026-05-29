from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from typing import Any

from src.domain.models import Post, PostThesis, Thesis, ThemeName
from src.extraction.company_extractor import extract_companies
from src.extraction.ticker_extractor import extract_tickers
from src.extraction.theme_extractor import classify_text

THESIS_MARKERS = (
    "bottleneck",
    "chokepoint",
    "supply chain",
    "misunderstood",
    "adoption",
    "beneficiary",
    "benefit",
    "accelerate",
    "matter",
)

RISK_MARKERS: dict[str, str] = {
    "risk": "General execution risk is explicitly mentioned",
    "struggle": "Incumbent technology may struggle to scale",
    "delay": "Adoption timeline may be delayed",
    "overbuild": "Cycle risk from potential overbuild",
    "competition": "Competitive pressure may cap upside",
}

MAX_SUMMARY_LEN = 280
LLMThesisCallable = Callable[[str], str | Mapping[str, Any]]


def _normalize_theme(value: object) -> ThemeName:
    if isinstance(value, ThemeName):
        return value
    if not isinstance(value, str):
        return ThemeName.UNKNOWN
    normalized = value.strip().lower()
    for theme in ThemeName:
        if theme.value.lower() == normalized or theme.name.lower() == normalized:
            return theme
    return ThemeName.UNKNOWN


def _candidate_sentences(text: str) -> list[str]:
    segments = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+|\n+", text) if segment.strip()]
    return segments or [text.strip()]


def _score_sentence(sentence: str) -> int:
    lower = sentence.lower()
    marker_score = sum(2 for marker in THESIS_MARKERS if marker in lower)
    causal_score = 2 if ("because" in lower or "therefore" in lower or "so that" in lower) else 0
    ticker_score = 2 if extract_tickers(sentence) else 0
    return marker_score + causal_score + ticker_score


def _extract_beneficiaries(text: str) -> list[str]:
    beneficiaries = set(extract_tickers(text))
    for ticker in extract_companies(text).values():
        if ticker:
            beneficiaries.add(ticker)
    return sorted(beneficiaries)


def _extract_risks(text: str) -> list[str]:
    lower = text.lower()
    risks: list[str] = []
    for marker, description in RISK_MARKERS.items():
        if marker in lower and description not in risks:
            risks.append(description)
    if "if " in lower and "risk" not in lower:
        risks.append("Outcome is conditional on adoption or execution assumptions")
    return risks


def _heuristic_thesis_from_post(post: Post) -> Thesis:
    sentences = _candidate_sentences(post.text)
    best_sentence = max(sentences, key=lambda sentence: (_score_sentence(sentence), len(sentence)))
    summary = best_sentence if len(best_sentence) <= MAX_SUMMARY_LEN else best_sentence[: MAX_SUMMARY_LEN - 3] + "..."
    themes = classify_text(post.text)
    top_theme = themes[0][0] if themes else ThemeName.UNKNOWN
    beneficiaries = _extract_beneficiaries(post.text)
    risks = _extract_risks(post.text)

    confidence = 0.5
    if top_theme != ThemeName.UNKNOWN:
        confidence += 0.1
    if beneficiaries:
        confidence += 0.1
    if _score_sentence(best_sentence) >= 4:
        confidence += 0.1
    confidence = min(0.95, confidence)

    return Thesis(
        summary=summary,
        theme=top_theme,
        beneficiaries=beneficiaries,
        risks=risks,
        confidence=confidence,
    )


def _build_llm_prompt(post: Post) -> str:
    allowed_themes = ", ".join(theme.value for theme in ThemeName)
    return (
        "Extract one investment thesis from the post and return JSON with keys: "
        '"summary", "theme", "beneficiaries", "risks", "confidence". '
        f"Allowed theme values: {allowed_themes}. "
        "Beneficiaries must be a list of stock tickers without $. "
        "Confidence must be a float between 0 and 1.\n\n"
        f"Post:\n{post.text}"
    )


def _parse_llm_thesis(payload: str | Mapping[str, Any]) -> Thesis:
    parsed: object = payload
    if isinstance(payload, str):
        parsed = json.loads(payload)
    if not isinstance(parsed, Mapping):
        raise ValueError("LLM thesis payload must be a JSON object")

    summary_raw = parsed.get("summary", "")
    summary = str(summary_raw).strip()
    if not summary:
        raise ValueError("LLM thesis summary is empty")

    beneficiaries = sorted(
        {
            str(item).upper().replace("$", "").strip()
            for item in parsed.get("beneficiaries", [])
            if isinstance(item, str) and item.strip()
        }
    )
    risks = [str(item).strip() for item in parsed.get("risks", []) if isinstance(item, str) and item.strip()]

    confidence_raw = parsed.get("confidence", 0.5)
    confidence = float(confidence_raw) if isinstance(confidence_raw, int | float | str) else 0.5
    confidence = max(0.0, min(1.0, confidence))

    return Thesis(
        summary=summary,
        theme=_normalize_theme(parsed.get("theme")),
        beneficiaries=beneficiaries,
        risks=risks,
        confidence=confidence,
    )


def extract_thesis_from_post(post: Post, llm_callable: LLMThesisCallable | None = None) -> Thesis:
    if llm_callable is not None:
        try:
            llm_result = llm_callable(_build_llm_prompt(post))
            thesis = _parse_llm_thesis(llm_result)
            if not thesis.beneficiaries:
                thesis.beneficiaries = _extract_beneficiaries(post.text)
            if thesis.theme == ThemeName.UNKNOWN:
                fallback = classify_text(post.text)
                thesis.theme = fallback[0][0] if fallback else ThemeName.UNKNOWN
            return thesis
        except Exception:
            pass
    return _heuristic_thesis_from_post(post)


def extract_post_theses(posts: list[Post], llm_callable: LLMThesisCallable | None = None) -> list[PostThesis]:
    extracted: list[PostThesis] = []
    for post in posts:
        thesis = extract_thesis_from_post(post, llm_callable=llm_callable)
        extracted.append(
            PostThesis(
                post_external_id=post.external_id,
                summary=thesis.summary,
                theme=thesis.theme,
                beneficiaries=thesis.beneficiaries,
                risks=thesis.risks,
                confidence=thesis.confidence,
            )
        )
    return extracted


def simple_thesis_from_post(post: Post) -> Thesis:
    # Backward-compatible wrapper used by report generation.
    return extract_thesis_from_post(post)
