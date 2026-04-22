"""
Eval harness: POST each ground-truth case to the live API and score results.

Usage:
    python scripts/run_eval.py [--api-url URL] [--ground-truth PATH]

Scoring:
    - Traffic-light match  (pass/fail per case)
    - Finding coverage     (each expected clause must appear in actual findings,
                            matched by keyword overlap in title + explanation + source_quote)
"""

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).parent.parent
DEFAULT_GT = ROOT / "tests" / "eval" / "ground_truth.json"
DEFAULT_URL = "https://backend-production-1d50.up.railway.app"


def keywords_found(expected_keywords: list[str], finding: dict) -> bool:
    haystack = " ".join([
        finding.get("title", ""),
        finding.get("explanation", ""),
        finding.get("source_quote", ""),
    ]).lower()
    return all(kw.lower() in haystack for kw in expected_keywords)


def score_case(case: dict, response: dict) -> dict:
    expected = case["expected"]
    actual_light = response.get("traffic_light", "")
    actual_findings = response.get("findings", [])

    checks = []

    # 1. Traffic-light check
    tl_pass = actual_light == expected["traffic_light"]
    checks.append({
        "check": "traffic_light",
        "expected": expected["traffic_light"],
        "actual": actual_light,
        "pass": tl_pass,
    })

    # 2. Finding coverage checks
    for clause in expected.get("must_flag", []):
        matched = any(keywords_found(clause["keywords"], f) for f in actual_findings)
        # Also check risk level on matched findings
        risk_ok = True
        if matched:
            matched_findings = [f for f in actual_findings if keywords_found(clause["keywords"], f)]
            risk_ok = any(f.get("risk") == clause["risk"] for f in matched_findings)
        checks.append({
            "check": f"clause: {clause['topic']}",
            "expected_risk": clause["risk"],
            "found": matched,
            "risk_correct": risk_ok,
            "pass": matched and risk_ok,
        })

    passed = sum(1 for c in checks if c["pass"])
    return {"case_id": case["id"], "checks": checks, "passed": passed, "total": len(checks)}


def run_eval(api_url: str, gt_path: Path, verbose: bool = False) -> None:
    cases = json.loads(gt_path.read_text(encoding="utf-8"))
    print(f"\nTermsGuard AI — Eval Harness")
    print(f"API: {api_url}")
    print(f"Cases: {len(cases)}")
    print("=" * 60)

    grand_passed = grand_total = 0

    with httpx.Client(timeout=180.0) as client:
        for case in cases:
            print(f"\n[{case['id']}] {case['title']}")
            t0 = time.time()
            try:
                resp = client.post(
                    f"{api_url}/api/v1/analyze",
                    json=case["input"],
                )
                resp.raise_for_status()
                response = resp.json()
                elapsed = time.time() - t0
            except Exception as exc:
                print(f"  ERROR: {exc}")
                continue

            result = score_case(case, response)
            grand_passed += result["passed"]
            grand_total += result["total"]

            for c in result["checks"]:
                icon = "PASS" if c["pass"] else "FAIL"
                print(f"  [{icon}] {c['check']}")
                if verbose and not c["pass"]:
                    findings = response.get("findings", [])
                    print(f"         traffic_light={response.get('traffic_light')!r}")
                    for i, f in enumerate(findings):
                        print(f"         finding[{i}] risk={f.get('risk')!r} title={f.get('title')!r}")
                        print(f"                  explanation={f.get('explanation', '')[:80]!r}")

            score_pct = 100 * result["passed"] // result["total"] if result["total"] else 0
            print(f"  Score: {result['passed']}/{result['total']} ({score_pct}%) — {elapsed:.1f}s")

    print("\n" + "=" * 60)
    if grand_total:
        overall = 100 * grand_passed // grand_total
        print(f"OVERALL: {grand_passed}/{grand_total} checks passed ({overall}%)")
        print("RESULT:", "PASS" if overall >= 70 else "FAIL")
    else:
        print("No checks ran.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TermsGuard AI eval harness")
    parser.add_argument("--api-url", default=DEFAULT_URL)
    parser.add_argument("--ground-truth", type=Path, default=DEFAULT_GT)
    parser.add_argument("--verbose", "-v", action="store_true", help="Show actual findings on failure")
    args = parser.parse_args()
    run_eval(args.api_url, args.ground_truth, verbose=args.verbose)
