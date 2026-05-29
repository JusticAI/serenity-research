from pathlib import Path

from src.domain.models import Post
from src.extraction.prediction_extractor import extract_post_predictions
from src.extraction.thesis_extractor import extract_post_theses
from src.extraction.theme_extractor import extract_theme_matches
from src.extraction.ticker_extractor import extract_ticker_mentions
from src.reporting.markdown_report import generate_markdown_report
from src.storage.db import (
    connect,
    fetch_posts,
    init_db,
    replace_predictions,
    replace_theme_matches,
    replace_theses,
    replace_ticker_mentions,
    upsert_posts,
)


def test_db_roundtrip_and_analysis(tmp_path: Path):
    conn = connect(tmp_path / "test.db")
    init_db(conn)
    posts = [Post(external_id="1", text="If photonics demand accelerates, $AAOI could benefit next year.")]
    assert upsert_posts(conn, posts) == 1
    loaded = fetch_posts(conn)
    assert len(loaded) == 1
    replace_ticker_mentions(conn, extract_ticker_mentions(loaded))
    replace_theme_matches(conn, extract_theme_matches(loaded))
    replace_theses(conn, extract_post_theses(loaded))
    replace_predictions(conn, extract_post_predictions(loaded))
    assert conn.execute("SELECT COUNT(*) FROM theses").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0] >= 1


def test_generate_report(tmp_path: Path):
    posts = [Post(external_id="1", text="If AI datacenter optical demand accelerates, $AAOI could benefit.")]
    out = generate_markdown_report(posts, tmp_path / "report.md")
    text = out.read_text(encoding="utf-8")
    assert "Serenity Research Report" in text
    assert "AAOI" in text
    assert "Extracted Predictions" in text
