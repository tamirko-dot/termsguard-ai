"""
Pytest wrapper for the eval harness — hits the live API.

Skip in fast CI with: pytest -m "not eval"
Run standalone:       pytest tests/eval/ -v -m eval

Override API endpoint: EVAL_API_URL=http://localhost:8000 pytest tests/eval/ -m eval
"""

import json
import os
from pathlib import Path

import httpx
import pytest

GT_PATH = Path(__file__).parent / "ground_truth.json"
DEFAULT_API = "https://backend-production-1d50.up.railway.app"

_CASES = json.loads(GT_PATH.read_text(encoding="utf-8"))


def _api_url() -> str:
    return os.environ.get("EVAL_API_URL", DEFAULT_API)


def _keywords_found(keywords: list[str], finding: dict) -> bool:
    haystack = " ".join([
        finding.get("title", ""),
        finding.get("explanation", ""),
        finding.get("source_quote", ""),
    ]).lower()
    return all(kw.lower() in haystack for kw in keywords)


@pytest.fixture(scope="module")
def live_responses() -> dict[str, dict]:
    url = _api_url()
    responses: dict[str, dict] = {}
    with httpx.Client(timeout=180.0) as client:
        for case in _CASES:
            resp = client.post(f"{url}/api/v1/analyze", json=case["input"])
            resp.raise_for_status()
            responses[case["id"]] = resp.json()
    return responses


@pytest.mark.eval
@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_traffic_light(case: dict, live_responses: dict) -> None:
    actual = live_responses[case["id"]].get("traffic_light")
    assert actual == case["expected"]["traffic_light"], (
        f"[{case['id']}] traffic_light: expected {case['expected']['traffic_light']!r}, got {actual!r}"
    )


@pytest.mark.eval
@pytest.mark.parametrize(
    "case,clause",
    [
        (case, clause)
        for case in _CASES
        for clause in case["expected"].get("must_flag", [])
    ],
    ids=[
        f"{case['id']}::{clause['topic'][:40]}"
        for case in _CASES
        for clause in case["expected"].get("must_flag", [])
    ],
)
def test_clause_flagged(case: dict, clause: dict, live_responses: dict) -> None:
    findings = live_responses[case["id"]].get("findings", [])
    matched = [f for f in findings if _keywords_found(clause["keywords"], f)]
    assert matched, (
        f"[{case['id']}] clause not found: {clause['topic']!r} "
        f"(keywords: {clause['keywords']})"
    )
    risks = {f.get("risk") for f in matched}
    assert clause["risk"] in risks, (
        f"[{case['id']}] clause {clause['topic']!r} found but risk mismatch: "
        f"expected {clause['risk']!r}, got {risks}"
    )
