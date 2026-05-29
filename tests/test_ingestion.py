from pathlib import Path

from src.ingestion.import_csv import load_posts_from_csv


def test_load_posts_from_csv(tmp_path: Path):
    csv = tmp_path / "tweets.csv"
    csv.write_text("tweet_id,text,likes\n1,hello $NVDA,10\n1,duplicate,11\n", encoding="utf-8")
    posts = load_posts_from_csv(csv)
    assert len(posts) == 1
    assert posts[0].external_id == "1"
    assert posts[0].likes == 10
