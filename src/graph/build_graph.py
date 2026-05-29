from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from src.domain.models import Post
from src.extraction.prediction_extractor import extract_predictions_from_post
from src.extraction.thesis_extractor import extract_thesis_from_post
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

        thesis = extract_thesis_from_post(post)
        thesis_node = f"thesis:{post.external_id}"
        graph.add_node(
            thesis_node,
            type="Thesis",
            summary=thesis.summary,
            confidence=thesis.confidence,
        )
        graph.add_edge(post_node, thesis_node, relationship="HAS_THESIS")

        thesis_theme_node = f"theme:{thesis.theme.value}"
        graph.add_node(thesis_theme_node, type="Theme", name=thesis.theme.value)
        graph.add_edge(thesis_node, thesis_theme_node, relationship="FOCUSES_ON")

        for ticker in thesis.beneficiaries:
            ticker_node = f"ticker:{ticker}"
            graph.add_node(ticker_node, type="Ticker", name=ticker)
            graph.add_edge(thesis_node, ticker_node, relationship="IDENTIFIES_BENEFICIARY")

        for risk_idx, risk in enumerate(thesis.risks, start=1):
            risk_node = f"risk:{post.external_id}:{risk_idx}"
            graph.add_node(risk_node, type="Risk", text=risk)
            graph.add_edge(thesis_node, risk_node, relationship="FLAGS_RISK")

        predictions = extract_predictions_from_post(post)
        for idx, prediction in enumerate(predictions, start=1):
            prediction_node = f"prediction:{post.external_id}:{idx}"
            graph.add_node(
                prediction_node,
                type="Prediction",
                text=prediction.text,
                direction=prediction.direction.value,
                confidence=prediction.confidence,
                condition=prediction.condition,
                horizon=prediction.horizon,
                status=prediction.status,
            )
            graph.add_edge(post_node, prediction_node, relationship="MAKES_PREDICTION")

            for ticker in extract_tickers(prediction.text):
                ticker_node = f"ticker:{ticker}"
                graph.add_node(ticker_node, type="Ticker", name=ticker)
                graph.add_edge(prediction_node, ticker_node, relationship="TARGETS")

            if prediction.condition:
                condition_node = f"condition:{post.external_id}:{idx}"
                graph.add_node(condition_node, type="Condition", text=prediction.condition)
                graph.add_edge(prediction_node, condition_node, relationship="HAS_CONDITION")
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
