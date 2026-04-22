import json

from app.crew.orchestrator import _parse_report
from app.models.document import DocMeta
from app.models.finding import RiskLevel


def _make_meta() -> DocMeta:
    return DocMeta(url="https://example.com/tos", length=500)


def test_parse_report_valid_json():
    payload = {
        "traffic_light": "red",
        "summary": "This ToS has serious issues.",
        "findings": [
            {
                "title": "Binding Arbitration",
                "explanation": "You cannot sue in court.",
                "risk": "red",
                "source_quote": "you waive your right to a jury trial",
                "char_start": 10,
                "char_end": 50,
            }
        ],
    }
    report = _parse_report(json.dumps(payload), _make_meta(), 1234)
    assert report.traffic_light == RiskLevel.RED
    assert len(report.findings) == 1
    assert report.findings[0].title == "Binding Arbitration"
    assert report.processing_ms == 1234


def test_parse_report_strips_markdown_fences():
    payload = {
        "traffic_light": "yellow",
        "summary": "Some concerns.",
        "findings": [],
    }
    raw = f"```json\n{json.dumps(payload)}\n```"
    report = _parse_report(raw, _make_meta(), 500)
    assert report.traffic_light == RiskLevel.YELLOW


def test_parse_report_returns_red_on_invalid_json():
    report = _parse_report("not valid json at all", _make_meta(), 0)
    assert report.traffic_light == RiskLevel.RED
    assert report.findings == []


def test_parse_report_preserves_doc_meta():
    meta = _make_meta()
    payload = {"traffic_light": "green", "summary": "Looks fine.", "findings": []}
    report = _parse_report(json.dumps(payload), meta, 100)
    assert report.doc_meta.url == "https://example.com/tos"
