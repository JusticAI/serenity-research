from src.domain.models import Post, ThemeName
from src.extraction.theme_extractor import classify_text
from src.extraction.ticker_extractor import extract_tickers, extract_ticker_mentions


def test_extract_tickers():
    assert extract_tickers("$NVDA and $AAOI, not $TOOLONG") == ["AAOI", "NVDA"]


def test_classify_photonics_and_networking():
    matches = classify_text("AI datacenter bandwidth needs optical interconnects and photonics")
    themes = {theme for theme, _ in matches}
    assert ThemeName.PHOTONICS in themes
    assert ThemeName.NETWORKING in themes


def test_extract_ticker_mentions():
    posts = [Post(external_id="1", text="Look at $AXTI and $MRVL")]
    mentions = extract_ticker_mentions(posts)
    assert {m.ticker for m in mentions} == {"AXTI", "MRVL"}
