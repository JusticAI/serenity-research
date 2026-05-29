from pathlib import Path
import json

from src.domain.models import Post
from src.graph.build_graph import export_graph_json


def test_export_graph_json(tmp_path: Path):
    out = export_graph_json(
        [Post(external_id="1", text="If optical demand accelerates, $AAOI could matter more next year.")],
        tmp_path / "graph.json",
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["nodes"]
    assert payload["edges"]
    node_types = {node["type"] for node in payload["nodes"]}
    assert "Thesis" in node_types
    assert "Prediction" in node_types
    relationships = {edge["relationship"] for edge in payload["edges"]}
    assert "HAS_THESIS" in relationships
    assert "MAKES_PREDICTION" in relationships
