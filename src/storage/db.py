from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from src.domain.models import Post, PostPrediction, PostThesis, ThemeMatch, TickerMention

DEFAULT_DB_PATH = Path("data/processed/serenity.db")
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    _ensure_column(conn, "theses", "beneficiaries_json", "TEXT DEFAULT '[]'")
    _ensure_column(conn, "theses", "risks_json", "TEXT DEFAULT '[]'")
    _ensure_column(conn, "predictions", "direction", "TEXT DEFAULT 'uncertain'")
    _ensure_column(conn, "predictions", "condition_text", "TEXT")
    _ensure_column(conn, "predictions", "horizon", "TEXT")
    _ensure_column(conn, "predictions", "confidence", "REAL DEFAULT 0.45")
    conn.commit()


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    if column_name in _table_columns(conn, table_name):
        return
    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def upsert_posts(conn: sqlite3.Connection, posts: Iterable[Post]) -> int:
    count = 0
    for post in posts:
        conn.execute(
            """
            INSERT INTO posts (external_id, created_at, author, text, url, likes, reposts, replies, quotes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(external_id) DO UPDATE SET
                created_at=excluded.created_at,
                author=excluded.author,
                text=excluded.text,
                url=excluded.url,
                likes=excluded.likes,
                reposts=excluded.reposts,
                replies=excluded.replies,
                quotes=excluded.quotes
            """,
            (
                post.external_id,
                post.created_at.isoformat() if post.created_at else None,
                post.author,
                post.text,
                post.url,
                post.likes,
                post.reposts,
                post.replies,
                post.quotes,
            ),
        )
        count += 1
    conn.commit()
    return count


def fetch_posts(conn: sqlite3.Connection) -> list[Post]:
    rows = conn.execute("SELECT * FROM posts ORDER BY COALESCE(created_at, '') ASC").fetchall()
    return [
        Post(
            external_id=row["external_id"],
            created_at=None if row["created_at"] is None else datetime.fromisoformat(row["created_at"]),
            author=row["author"],
            text=row["text"],
            url=row["url"],
            likes=row["likes"],
            reposts=row["reposts"],
            replies=row["replies"],
            quotes=row["quotes"],
        )
        for row in rows
    ]


def replace_ticker_mentions(conn: sqlite3.Connection, mentions: Iterable[TickerMention]) -> None:
    conn.execute("DELETE FROM ticker_mentions")
    conn.executemany(
        "INSERT OR IGNORE INTO ticker_mentions (ticker, post_external_id) VALUES (?, ?)",
        [(m.ticker, m.post_external_id) for m in mentions],
    )
    conn.commit()


def replace_theme_matches(conn: sqlite3.Connection, matches: Iterable[ThemeMatch]) -> None:
    conn.execute("DELETE FROM theme_matches")
    conn.executemany(
        "INSERT OR IGNORE INTO theme_matches (theme, post_external_id, score) VALUES (?, ?, ?)",
        [(m.theme.value, m.post_external_id, m.score) for m in matches],
    )
    conn.commit()


def replace_theses(conn: sqlite3.Connection, theses: Iterable[PostThesis]) -> None:
    conn.execute("DELETE FROM theses")
    conn.executemany(
        """
        INSERT INTO theses (
            post_external_id,
            summary,
            theme,
            confidence,
            beneficiaries_json,
            risks_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                thesis.post_external_id,
                thesis.summary,
                thesis.theme.value,
                thesis.confidence,
                json.dumps(thesis.beneficiaries, ensure_ascii=False),
                json.dumps(thesis.risks, ensure_ascii=False),
            )
            for thesis in theses
        ],
    )
    conn.commit()


def replace_predictions(conn: sqlite3.Connection, predictions: Iterable[PostPrediction]) -> None:
    conn.execute("DELETE FROM predictions")
    conn.executemany(
        """
        INSERT INTO predictions (
            post_external_id,
            prediction_text,
            prediction_date,
            status,
            direction,
            condition_text,
            horizon,
            confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                prediction.post_external_id,
                prediction.text,
                prediction.horizon,
                prediction.status,
                prediction.direction.value,
                prediction.condition,
                prediction.horizon,
                prediction.confidence,
            )
            for prediction in predictions
        ],
    )
    conn.commit()


def query_ticker(conn: sqlite3.Connection, ticker: str) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT p.* FROM posts p
        JOIN ticker_mentions tm ON tm.post_external_id = p.external_id
        WHERE UPPER(tm.ticker) = UPPER(?)
        ORDER BY COALESCE(p.created_at, '') ASC
        """,
        (ticker.replace("$", ""),),
    ).fetchall()


def query_theme(conn: sqlite3.Connection, theme: str) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT p.*, tm.score FROM posts p
        JOIN theme_matches tm ON tm.post_external_id = p.external_id
        WHERE LOWER(tm.theme) = LOWER(?)
        ORDER BY tm.score DESC, COALESCE(p.created_at, '') ASC
        """,
        (theme,),
    ).fetchall()
