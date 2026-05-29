from src.domain.models import Post, PredictionDirection, ThemeName
from src.extraction.prediction_extractor import extract_post_predictions, extract_predictions_from_post, looks_like_prediction
from src.extraction.thesis_extractor import extract_post_theses, extract_thesis_from_post, simple_thesis_from_post
from src.extraction.theme_extractor import classify_text
from src.extraction.ticker_extractor import extract_tickers, extract_ticker_mentions


def test_extract_tickers():
    assert extract_tickers("$NVDA and $AAOI, not $TOOLONG") == ["AAOI", "NVDA"]


def test_classify_photonics_and_networking():
    matches = classify_text("AI datacenter bandwidth needs optical interconnects and photonics")
    themes = {theme for theme, _ in matches}
    assert ThemeName.PHOTONICS in themes
    assert ThemeName.NETWORKING in themes


def test_extract_ticker_mentions():
    posts = [Post(external_id="1", text="Look at $AXTI and $MRVL")]
    mentions = extract_ticker_mentions(posts)
    assert {m.ticker for m in mentions} == {"AXTI", "MRVL"}


def test_simple_thesis_contains_theme_and_beneficiary():
    post = Post(
        external_id="1",
        text="AI datacenter bottleneck is optical interconnect capacity and $AAOI could be a beneficiary.",
    )
    thesis = simple_thesis_from_post(post)
    assert thesis.theme in {ThemeName.PHOTONICS, ThemeName.NETWORKING, ThemeName.AI, ThemeName.DATACENTER}
    assert "AAOI" in thesis.beneficiaries
    assert thesis.summary


def test_extract_thesis_from_llm_payload():
    post = Post(external_id="1", text="Any text")

    def mock_llm(_: str) -> str:
        return (
            '{"summary":"Optical bottlenecks could favor AAOI",'
            '"theme":"Photonics",'
            '"beneficiaries":["AAOI"],'
            '"risks":["Execution risk"],'
            '"confidence":0.82}'
        )

    thesis = extract_thesis_from_post(post, llm_callable=mock_llm)
    assert thesis.theme == ThemeName.PHOTONICS
    assert thesis.beneficiaries == ["AAOI"]
    assert thesis.confidence == 0.82


def test_extract_post_theses_batch():
    posts = [Post(external_id="1", text="If CPO adoption accelerates, materials names like $AXTI may benefit.")]
    theses = extract_post_theses(posts)
    assert len(theses) == 1
    assert theses[0].post_external_id == "1"
    assert theses[0].summary


def test_prediction_extraction_shape():
    post = Post(
        external_id="1",
        text="If CPO adoption accelerates, $AXTI could matter more in the next year.",
    )
    predictions = extract_predictions_from_post(post)
    assert len(predictions) == 1
    prediction = predictions[0]
    assert prediction.direction in {PredictionDirection.BULLISH, PredictionDirection.CONDITIONAL}
    assert prediction.condition is not None
    assert prediction.horizon is not None
    assert prediction.confidence > 0


def test_extract_post_predictions_batch():
    posts = [
        Post(external_id="1", text="If bandwidth demand accelerates, $AAOI could benefit."),
        Post(external_id="2", text="No forward-looking statement here."),
    ]
    predictions = extract_post_predictions(posts)
    assert len(predictions) == 1
    assert predictions[0].post_external_id == "1"


def test_looks_like_prediction():
    assert looks_like_prediction("Demand will likely accelerate next year.")
    assert not looks_like_prediction("Photonics and networking are interesting themes.")
