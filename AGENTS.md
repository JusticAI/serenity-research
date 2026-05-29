# AGENTS.md

## Mission

Build an Investor OS: a reusable research system for extracting investment logic from public posts, essays, transcripts, and notes.

The first target is Serenity (`@aleabitoreddit`), but the architecture must support many analysts and KOLs.

## Core Principle

Do not build a ticker tracker. Build a thesis tracker.

Bad output:

- Serenity bought AAOI.

Good output:

- Serenity argued that AI datacenter bandwidth demand creates an optical interconnect bottleneck, making certain photonics suppliers potential beneficiaries.

## Code Standards

- Python 3.11+
- Type annotations everywhere practical.
- Pydantic for domain objects.
- SQLite for local durable storage.
- Typer for CLI.
- Pytest for tests.
- Ruff for linting.
- Keep modules small and composable.

## Forbidden

- Do not bypass website access restrictions.
- Do not scrape X in violation of rules.
- Do not hard-code Serenity-only assumptions into core abstractions.
- Do not present outputs as investment advice.

## Extension Points

- Add new data sources by implementing a loader that returns `list[Post]`.
- Add better extraction by replacing keyword rules with an LLM provider.
- Add prediction validation by integrating market data later.
- Add more graph relationships without changing imported raw post records.

## Useful Commands

```bash
pip install -e ".[dev]"
pytest
ruff check .
serenity import data/raw/sample_tweets.csv
serenity analyze
serenity report
serenity graph
```
