from __future__ import annotations

KNOWN_COMPANIES = {
    "nvidia": "NVDA",
    "marvell": "MRVL",
    "broadcom": "AVGO",
    "coherent": "COHR",
    "lumentum": "LITE",
    "applied optoelectronics": "AAOI",
    "axt": "AXTI",
    "silicon photonics": None,
}


def extract_companies(text: str) -> dict[str, str | None]:
    lower = text.lower()
    return {name: ticker for name, ticker in KNOWN_COMPANIES.items() if name in lower}
