from __future__ import annotations

from pathlib import Path

from src.analysis.failure_case_analysis import failure_review_placeholder
from src.analysis.success_case_analysis import candidate_success_cases
from src.analysis.timeline_analysis import posts_by_year
from src.analysis.topic_analysis import theme_counts, ticker_counts
from src.domain.models import Post
from src.extraction.thesis_extractor import simple_thesis_from_post


def _top_lines(items: list[tuple[str, int]], empty: str = "No data") -> str:
    if not items:
        return f"- {empty}\n"
    return "".join(f"- {name}: {count}\n" for name, count in items)


def generate_markdown_report(posts: list[Post], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    themes = theme_counts(posts).most_common(15)
    tickers = ticker_counts(posts).most_common(15)
    timeline = posts_by_year(posts)
    success_cases = candidate_success_cases(posts)
    theses = [simple_thesis_from_post(post) for post in posts[:20]]

    lines: list[str] = []
    lines.append("# Serenity Research Report\n\n")
    lines.append("## Executive Summary\n\n")
    lines.append(
        "This report summarizes imported public posts and extracts a first-pass view of recurring investment themes, tickers, and thesis patterns. "
        "The MVP uses deterministic rules; deeper LLM-based thesis extraction should be added in Phase 2.\n\n"
    )

    lines.append("## Core Investment Philosophy Detected\n\n")
    lines.append("A recurring framework appears to be:\n\n")
    lines.append("```text\n")
    lines.append("Technology trend\n  -> supply-chain decomposition\n  -> bottleneck/chokepoint identification\n  -> misunderstood beneficiary\n  -> market recognition\n  -> valuation rerating\n")
    lines.append("```\n\n")

    lines.append("## Top Themes\n\n")
    lines.append(_top_lines(themes))
    lines.append("\n## Top Tickers\n\n")
    lines.append(_top_lines(tickers, empty="No ticker mentions found"))

    lines.append("\n## Industry Map Draft\n\n")
    lines.append("```text\n")
    lines.append("AI Infrastructure\n")
    lines.append("├── GPU / Accelerators\n")
    lines.append("├── Datacenter Networking\n")
    lines.append("├── Optical Interconnects / Photonics\n")
    lines.append("├── CPO and Transceivers\n")
    lines.append("├── Materials such as InP substrates\n")
    lines.append("└── Power, cooling, and physical infrastructure\n")
    lines.append("```\n")

    lines.append("\n## Representative Thesis Objects\n\n")
    for thesis in theses:
        beneficiaries = ", ".join(thesis.beneficiaries) or "n/a"
        risks = ", ".join(thesis.risks) or "n/a"
        lines.append(f"- Theme: **{thesis.theme.value}** | Beneficiaries: `{beneficiaries}` | Risks: {risks}\n")
        lines.append(f"  - {thesis.summary}\n")

    lines.append("\n## Timeline\n\n")
    for year, year_posts in timeline.items():
        lines.append(f"### {year}\n\n")
        for post in year_posts[:10]:
            date = post.created_at.date().isoformat() if post.created_at else "unknown date"
            lines.append(f"- {date}: {post.text[:220]}\n")
        lines.append("\n")

    lines.append("## Candidate Success Cases\n\n")
    if success_cases:
        for ticker, texts in sorted(success_cases.items()):
            lines.append(f"### {ticker}\n\n")
            lines.append(f"Mentioned in {len(texts)} imported post(s). First thesis snippet:\n\n")
            lines.append(f"> {texts[0][:350]}\n\n")
    else:
        lines.append("No ticker-linked cases found.\n\n")

    lines.append("## Failure or Unverified Cases\n\n")
    lines.append(f"{failure_review_placeholder()}\n\n")

    lines.append("## Next Steps\n\n")
    lines.append("- Add LLM-based thesis extraction.\n")
    lines.append("- Add market-data validation for predictions.\n")
    lines.append("- Add multi-analyst profiles.\n")
    lines.append("- Add Streamlit dashboard.\n")
    lines.append("- Add richer knowledge graph visualization.\n")

    path.write_text("".join(lines), encoding="utf-8")
    return path
