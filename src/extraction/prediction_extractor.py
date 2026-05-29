from __future__ import annotations

import re

from src.domain.models import Post, PostPrediction, Prediction, PredictionDirection

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
PREDICTION_MARKERS = (
    "will",
    "could",
    "may",
    "should",
    "expect",
    "forecast",
    "likely",
    "unlikely",
    "target",
    "if",
    "when",
)

BULLISH_MARKERS = ("accelerate", "benefit", "upside", "winner", "rerating", "outperform", "matter more")
BEARISH_MARKERS = ("struggle", "risk", "downside", "headwind", "decline", "slowdown", "miss")

HORIZON_PATTERNS = (
    re.compile(r"\bnext quarter\b", flags=re.IGNORECASE),
    re.compile(r"\bnext year\b", flags=re.IGNORECASE),
    re.compile(r"\bthis year\b", flags=re.IGNORECASE),
    re.compile(r"\b(?:in|within)\s+\d+\s+(?:day|days|month|months|quarter|quarters|year|years)\b", flags=re.IGNORECASE),
    re.compile(r"\bby\s+(?:20\d{2}|q[1-4])\b", flags=re.IGNORECASE),
    re.compile(r"\b(?:near|mid|long)\s*-?\s*term\b", flags=re.IGNORECASE),
)


def _split_sentences(text: str) -> list[str]:
    sentences = [segment.strip() for segment in SENTENCE_SPLIT.split(text) if segment.strip()]
    return sentences or [text.strip()]


def looks_like_prediction(text: str) -> bool:
    lower = text.lower()
    return any(re.search(rf"\b{re.escape(marker)}\b", lower) for marker in PREDICTION_MARKERS)


def _extract_condition(sentence: str) -> str | None:
    for marker in ("if", "when"):
        match = re.search(rf"\b{marker}\s+([^.;!?]+)", sentence, flags=re.IGNORECASE)
        if match:
            condition = match.group(1).strip(" ,")
            if condition:
                return f"{marker} {condition}"
    return None


def _extract_horizon(sentence: str) -> str | None:
    for pattern in HORIZON_PATTERNS:
        match = pattern.search(sentence)
        if match:
            return match.group(0)
    return None


def _infer_direction(sentence: str, condition: str | None) -> PredictionDirection:
    lower = sentence.lower()
    bullish_hits = sum(1 for marker in BULLISH_MARKERS if marker in lower)
    bearish_hits = sum(1 for marker in BEARISH_MARKERS if marker in lower)
    if bullish_hits > bearish_hits:
        return PredictionDirection.BULLISH
    if bearish_hits > bullish_hits:
        return PredictionDirection.BEARISH
    if condition:
        return PredictionDirection.CONDITIONAL
    return PredictionDirection.UNCERTAIN


def _confidence(sentence: str, direction: PredictionDirection, horizon: str | None) -> float:
    score = 0.45
    if direction in {PredictionDirection.BULLISH, PredictionDirection.BEARISH}:
        score += 0.15
    elif direction is PredictionDirection.CONDITIONAL:
        score += 0.05
    if horizon:
        score += 0.1
    if "$" in sentence:
        score += 0.1
    if re.search(r"\b(may|could)\b", sentence, flags=re.IGNORECASE):
        score -= 0.05
    return max(0.2, min(0.95, score))


def extract_predictions_from_post(post: Post) -> list[Prediction]:
    predictions: list[Prediction] = []
    for sentence in _split_sentences(post.text):
        if not looks_like_prediction(sentence):
            continue
        text = sentence.strip()
        if not text:
            continue
        condition = _extract_condition(sentence)
        horizon = _extract_horizon(sentence)
        direction = _infer_direction(sentence, condition)
        predictions.append(
            Prediction(
                text=text,
                direction=direction,
                condition=condition,
                horizon=horizon,
                confidence=_confidence(sentence, direction, horizon),
            )
        )
    return predictions


def extract_post_predictions(posts: list[Post]) -> list[PostPrediction]:
    extracted: list[PostPrediction] = []
    for post in posts:
        for prediction in extract_predictions_from_post(post):
            extracted.append(
                PostPrediction(
                    post_external_id=post.external_id,
                    text=prediction.text,
                    direction=prediction.direction,
                    condition=prediction.condition,
                    horizon=prediction.horizon,
                    confidence=prediction.confidence,
                    status=prediction.status,
                )
            )
    return extracted
