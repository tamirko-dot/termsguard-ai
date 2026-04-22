import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 120.0


def analyze(raw_text: str, url: str | None = None, title: str | None = None) -> dict:
    """POST to /api/v1/analyze and return the parsed JSON response."""
    payload = {"raw_text": raw_text, "url": url, "title": title}
    with httpx.Client(timeout=TIMEOUT) as client:
        response = client.post(f"{API_BASE_URL}/api/v1/analyze", json=payload)
        response.raise_for_status()
        return response.json()


def health() -> dict:
    """GET /health and return parsed JSON."""
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        return response.json()
