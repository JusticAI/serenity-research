from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from src.domain.models import Post
from src.extraction.theme_extractor import classify_text
from src.extraction.ticker_extractor import extract_tickers


def build_graph(posts: list[Post]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for post in posts:
        post_node = f"post:{post.external_id}"
        graph.add_node(post_node, type="Post", text=post.text, author=post.author)
        for ticker in extract_tickers(post.text):
            ticker_node = f"ticker:{ticker}"
            graph.add_node(ticker_node, type="Ticker", name=ticker)
            graph.add_edge(post_node, ticker_node, relationship="MENTIONS")
        for theme, score in classify_text(post.text):
            theme_node = f"theme:{theme.value}"
            graph.add_node(theme_node, type="Theme", name=theme.value)
            graph.add_edge(post_node, theme_node, relationship="SUPPORTS", score=score)
    return graph


def export_graph_json(posts: list[Post], output_path: str | Path) -> Path:
    graph = build_graph(posts)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "nodes": [dict(id=node, **attrs) for node, attrs in graph.nodes(data=True)],
        "edges": [
            {"source": source, "target": target, **attrs}
            for source, target, attrs in graph.edges(data=True)
        ],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
