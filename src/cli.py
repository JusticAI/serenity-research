from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from src.extraction.theme_extractor import extract_theme_matches
from src.extraction.ticker_extractor import extract_ticker_mentions
from src.graph.build_graph import export_graph_json
from src.ingestion.import_csv import load_posts_from_csv
from src.ingestion.import_json import load_posts_from_json
from src.reporting.markdown_report import generate_markdown_report
from src.storage.db import (
    DEFAULT_DB_PATH,
    connect,
    fetch_posts,
    init_db,
    query_theme,
    query_ticker,
    replace_theme_matches,
    replace_ticker_mentions,
    upsert_posts,
)

app = typer.Typer(help="Investor OS for Serenity-style public post research.")
console = Console()


@app.command("import")
def import_posts(path: Path, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Import posts from CSV or JSON into SQLite."""
    if path.suffix.lower() == ".csv":
        posts = load_posts_from_csv(path)
    elif path.suffix.lower() == ".json":
        posts = load_posts_from_json(path)
    else:
        raise typer.BadParameter("Only .csv and .json are supported in MVP")

    conn = connect(db_path)
    init_db(conn)
    count = upsert_posts(conn, posts)
    console.print(f"Imported or updated {count} post(s) into {db_path}")


@app.command()
def analyze(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Run deterministic extraction for tickers and themes."""
    conn = connect(db_path)
    init_db(conn)
    posts = fetch_posts(conn)
    ticker_mentions = extract_ticker_mentions(posts)
    theme_matches = extract_theme_matches(posts)
    replace_ticker_mentions(conn, ticker_mentions)
    replace_theme_matches(conn, theme_matches)
    console.print(
        f"Analyzed {len(posts)} post(s): {len(ticker_mentions)} ticker mention(s), {len(theme_matches)} theme match(es)."
    )


@app.command()
def report(
    db_path: Path = DEFAULT_DB_PATH,
    output_path: Path = Path("reports/serenity_report.md"),
) -> None:
    """Generate Markdown research report."""
    conn = connect(db_path)
    init_db(conn)
    posts = fetch_posts(conn)
    path = generate_markdown_report(posts, output_path)
    console.print(f"Report written to {path}")


@app.command()
def ticker(symbol: str, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Show posts mentioning a ticker."""
    conn = connect(db_path)
    rows = query_ticker(conn, symbol)
    table = Table(title=f"Posts mentioning {symbol.upper().replace('$', '')}")
    table.add_column("Date")
    table.add_column("Author")
    table.add_column("Text")
    for row in rows:
        table.add_row(str(row["created_at"] or ""), row["author"], row["text"][:120])
    console.print(table)


@app.command()
def theme(name: str, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Show posts classified under a theme."""
    conn = connect(db_path)
    rows = query_theme(conn, name)
    table = Table(title=f"Posts under theme {name}")
    table.add_column("Score")
    table.add_column("Date")
    table.add_column("Text")
    for row in rows:
        table.add_row(str(row["score"]), str(row["created_at"] or ""), row["text"][:120])
    console.print(table)


@app.command()
def graph(
    db_path: Path = DEFAULT_DB_PATH,
    output_path: Path = Path("knowledge_graph/serenity_graph.json"),
) -> None:
    """Build a JSON knowledge graph."""
    conn = connect(db_path)
    posts = fetch_posts(conn)
    path = export_graph_json(posts, output_path)
    console.print(f"Graph written to {path}")


if __name__ == "__main__":
    app()
