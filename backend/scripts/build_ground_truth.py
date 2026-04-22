"""
Helper to bootstrap new ground-truth entries.

Submits a raw text to the API and prints a JSON template you can paste
into tests/eval/ground_truth.json, then fill in the expected fields.

Usage:
    python scripts/build_ground_truth.py --text "paste your ToS here..." --id case_005
    python scripts/build_ground_truth.py --file path/to/tos.txt --id case_005 --url https://...
"""

import argparse
import json
import sys
from pathlib import Path

import httpx

DEFAULT_API = "https://backend-production-1d50.up.railway.app"


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap a ground-truth entry from a live API call")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Raw text inline")
    src.add_argument("--file", type=Path, help="Path to a .txt file")
    parser.add_argument("--id", required=True, help="Case ID, e.g. case_005")
    parser.add_argument("--title", default="Untitled", help="Human-readable title for this case")
    parser.add_argument("--url", default=None, help="Source URL (optional)")
    parser.add_argument("--api-url", default=DEFAULT_API)
    args = parser.parse_args()

    raw_text = args.text if args.text else args.file.read_text(encoding="utf-8")

    payload = {"raw_text": raw_text, "url": args.url, "title": args.title}

    print(f"Calling {args.api_url}/api/v1/analyze …", file=sys.stderr)
    with httpx.Client(timeout=180.0) as client:
        resp = client.post(f"{args.api_url}/api/v1/analyze", json=payload)
        resp.raise_for_status()
        response = resp.json()

    must_flag = [
        {
            "topic": f["title"],
            "risk": f["risk"],
            "keywords": ["FILL_IN", "KEYWORDS"],
        }
        for f in response.get("findings", [])
    ]

    entry = {
        "id": args.id,
        "title": args.title,
        "input": payload,
        "expected": {
            "traffic_light": response.get("traffic_light", "FILL_IN"),
            "must_flag": must_flag,
        },
        "_actual_response": response,
    }

    print("\n# Paste this into ground_truth.json, then review and fill in keywords:\n")
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    print(
        "\n# NOTE: Remove _actual_response before committing. "
        "Adjust must_flag keywords to be specific enough to match future runs.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
