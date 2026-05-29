# Serenity Research

`serenity-research` is a local research system for studying the investment logic of public market commentators such as Serenity (`@aleabitoreddit`). The goal is not to mirror trades. The goal is to extract theses, supply-chain logic, themes, tickers, predictions, and reusable research frameworks.

> This project is for research and education only. It is not investment advice.

## MVP Features

- Import posts from user-provided CSV files.
- Store normalized posts in SQLite.
- Extract stock tickers such as `$NVDA`, `$AAOI`, `$AXTI`.
- Classify posts into simple keyword-based themes.
- Generate a Markdown research report.
- Query tickers and themes from the CLI.
- Build a basic knowledge graph.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Expected CSV Format

At minimum, the CSV should include a text column. Recommended columns:

```csv
tweet_id,created_at,author,text,url,like_count,repost_count,reply_count,quote_count
```

Aliases are supported for several common fields, including `id`, `date`, `content`, `likes`, `retweets`, and `replies`.

## Run

```bash
serenity import data/raw/sample_tweets.csv
serenity analyze
serenity report
serenity ticker AAOI
serenity theme Photonics
serenity graph
```

Or without installing scripts:

```bash
python -m src.cli import data/raw/sample_tweets.csv
python -m src.cli analyze
python -m src.cli report
```

## Outputs

- SQLite database: `data/processed/serenity.db`
- Markdown report: `reports/serenity_report.md`
- Knowledge graph: `knowledge_graph/serenity_graph.json`

## Architecture

The architecture is intentionally generic. Serenity is only the first analyst profile. Future profiles can be added by changing author metadata and input datasets.

Core modules:

- `domain/`: Pydantic models.
- `ingestion/`: CSV/JSON import and normalization.
- `storage/`: SQLite persistence.
- `extraction/`: ticker, company, theme, thesis, and prediction extraction.
- `analysis/`: timeline and case analysis.
- `graph/`: knowledge graph generation.
- `reporting/`: Markdown/HTML report generation.
- `cli.py`: Typer CLI.

## Research Principle

Do not stop at: Serenity mentioned `$AAOI`.

Ask: what thesis made `$AAOI` matter?

This project is designed around theses, not tickers.

## Limitations

- The MVP uses deterministic keyword rules, not a full LLM pipeline.
- X posts may be deleted, edited, unavailable, or incomplete.
- Imported datasets may be biased toward popular posts.
- Price validation and prediction accuracy review are placeholders in v0.1.
