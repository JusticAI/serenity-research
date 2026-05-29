from pathlib import Path

from src.domain.models import Post
from src.extraction.theme_extractor import extract_theme_matches
from src.extraction.ticker_extractor import extract_ticker_mentions
from src.reporting.markdown_report import generate_markdown_report
from src.storage.db import connect, fetch_posts, init_db, replace_theme_matches, replace_ticker_mentions, upsert_posts


def test_db_roundtrip_and_analysis(tmp_path: Path):
    conn = connect(tmp_path / "test.db")
    init_db(conn)
    posts = [Post(external_id="1", text="Photonics bottleneck $AAOI")]
    assert upsert_posts(conn, posts) == 1
    loaded = fetch_posts(conn)
    assert len(loaded) == 1
    replace_ticker_mentions(conn, extract_ticker_mentions(loaded))
    replace_theme_matches(conn, extract_theme_matches(loaded))


def test_generate_report(tmp_path: Path):
    posts = [Post(external_id="1", text="AI datacenter optical bottleneck $AAOI")]
    out = generate_markdown_report(posts, tmp_path / "report.md")
    text = out.read_text(encoding="utf-8")
    assert "Serenity Research Report" in text
    assert "AAOI" in text
