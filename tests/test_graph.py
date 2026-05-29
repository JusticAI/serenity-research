from pathlib import Path
import json

from src.domain.models import Post
from src.graph.build_graph import export_graph_json


def test_export_graph_json(tmp_path: Path):
    out = export_graph_json([Post(external_id="1", text="Photonics $AAOI")], tmp_path / "graph.json")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["nodes"]
    assert payload["edges"]
