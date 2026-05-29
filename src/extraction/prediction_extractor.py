from __future__ import annotations

PREDICTION_MARKERS = ["will", "could", "may", "should", "if", "when", "become", "accelerates"]


def looks_like_prediction(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in PREDICTION_MARKERS)
