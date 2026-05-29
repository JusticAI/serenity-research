from __future__ import annotations

from src.domain.models import Post, ThemeMatch, ThemeName

THEME_KEYWORDS: dict[ThemeName, list[str]] = {
    ThemeName.AI: ["ai", "artificial intelligence", "inference", "model", "gpu"],
    ThemeName.DATACENTER: ["datacenter", "data center", "rack", "cluster"],
    ThemeName.PHOTONICS: ["photonics", "laser", "optical interconnect", "light"],
    ThemeName.OPTICS: ["optics", "optical", "transceiver"],
    ThemeName.CPO: ["cpo", "co-packaged optics", "co packaged optics"],
    ThemeName.NETWORKING: ["networking", "switch", "bandwidth", "ethernet", "interconnect"],
    ThemeName.ROBOTICS: ["robot", "robotics", "humanoid", "actuator", "sensor"],
    ThemeName.POWER: ["power", "energy", "thermal", "cooling", "density"],
    ThemeName.SEMICONDUCTOR: ["semiconductor", "chip", "foundry", "wafer"],
    ThemeName.MATERIALS: ["materials", "substrate", "inp", "silicon", "gallium"],
    ThemeName.MACRO: ["rates", "inflation", "fed", "macro", "recession"],
    ThemeName.PORTFOLIO: ["position", "portfolio", "trade", "trim", "buy", "sell"],
    ThemeName.FRAMEWORK: ["framework", "chokepoint", "bottleneck", "misunderstood", "adoption curve"],
}


def classify_text(text: str) -> list[tuple[ThemeName, float]]:
    lower = text.lower()
    matches: list[tuple[ThemeName, float]] = []
    for theme, keywords in THEME_KEYWORDS.items():
        hits = sum(1 for keyword in keywords if keyword in lower)
        if hits:
            matches.append((theme, float(hits)))
    if not matches:
        return [(ThemeName.UNKNOWN, 1.0)]
    return sorted(matches, key=lambda item: item[1], reverse=True)


def extract_theme_matches(posts: list[Post]) -> list[ThemeMatch]:
    results: list[ThemeMatch] = []
    for post in posts:
        for theme, score in classify_text(post.text):
            results.append(ThemeMatch(theme=theme, post_external_id=post.external_id, score=score))
    return results
