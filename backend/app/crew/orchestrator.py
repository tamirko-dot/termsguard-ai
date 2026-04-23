import json
import logging
import re
import time

from crewai import Crew, Process

from app.crew.agents.analyst import build_analyst
from app.crew.agents.communicator import build_communicator
from app.crew.agents.extractor import build_extractor
from app.crew.tasks.analyze_task import build_analyze_task
from app.crew.tasks.communicate_task import build_communicate_task
from app.crew.tasks.extract_task import build_extract_task
from app.crew.tools.clause_classifier_tool import RED_KEYWORDS, YELLOW_KEYWORDS
from app.models.document import DocMeta, Document
from app.models.finding import Finding, RiskLevel
from app.models.report import Report

# Phrases that indicate a user-friendly clause — remove LLM findings whose
# source_quote contains any of these (false-positive filter).
_GREEN_INDICATORS = [
    "do not sell", "will not sell", "not sell", "never sell",
    "delete within 30", "delete it within", "deleted within",
    "permanently delete", "only for the duration of your account",
    "60 days in advance", "90 days in advance",
    "minimum data necessary", "only the minimum",
]

# Negation prefixes that flip a keyword match from risky to safe.
_NEGATIONS = ["not ", "no ", "never ", "don't ", "do not ", "will not ", "won't ", "cannot "]


def _has_negation(text: str, keyword_idx: int) -> bool:
    prefix = text[max(0, keyword_idx - 12):keyword_idx].lower()
    return any(neg in prefix for neg in _NEGATIONS)


def _classifier_scan(text: str, keywords: list[str]) -> list[tuple[str, int]]:
    """Return (keyword, char_idx) pairs found in text that are not negated."""
    lower = text.lower()
    hits = []
    for kw in keywords:
        idx = lower.find(kw)
        while idx != -1:
            if not _has_negation(lower, idx):
                hits.append((kw, idx))
            idx = lower.find(kw, idx + 1)
    return hits


def _post_process(report: Report, raw_text: str) -> Report:
    """Apply deterministic corrections on top of LLM output."""

    # ── Step 1: remove false-positive findings ────────────────────────────
    findings = [
        f for f in report.findings
        if not any(gi in f.source_quote.lower() for gi in _GREEN_INDICATORS)
    ]

    # ── Step 2: RED safety net — add any RED clause the LLM missed ────────
    sentences = re.split(r"(?<=[.;])\s+", raw_text)
    for sentence in sentences:
        if len(sentence.strip()) < 20:
            continue
        red_hits = _classifier_scan(sentence, RED_KEYWORDS)
        if not red_hits:
            continue
        # Skip if already covered by an existing finding
        already_covered = any(
            sentence[:40].lower() in f.source_quote.lower()
            or f.source_quote.lower()[:40] in sentence.lower()
            for f in findings
        )
        if already_covered:
            continue
        kw = red_hits[0][0]
        char_start = max(0, raw_text.lower().find(sentence[:30].lower()))
        findings.append(Finding(
            title=f"{kw.replace('-', ' ').title()} Clause",
            explanation=(
                f"This clause contains high-risk language ('{kw}'). "
                "It may significantly limit your rights."
            ),
            risk=RiskLevel.RED,
            source_quote=sentence.strip()[:300],
            char_start=char_start,
            char_end=char_start + len(sentence),
        ))

    # ── Step 3: recompute traffic_light from final findings ───────────────
    risks = {f.risk for f in findings}
    if RiskLevel.RED in risks:
        traffic_light = RiskLevel.RED
    elif RiskLevel.YELLOW in risks:
        traffic_light = RiskLevel.YELLOW
    else:
        traffic_light = RiskLevel.GREEN

    return Report(
        traffic_light=traffic_light,
        summary=report.summary,
        findings=findings,
        doc_meta=report.doc_meta,
        processing_ms=report.processing_ms,
    )

logger = logging.getLogger(__name__)


def run_pipeline(document: Document) -> Report:
    """Run the full Extractor → Analyst → Communicator pipeline and return a Report."""
    start_ms = time.monotonic()

    extractor = build_extractor()
    analyst = build_analyst()
    communicator = build_communicator()

    extract_task = build_extract_task(extractor, document.raw_text)
    analyze_task = build_analyze_task(analyst, extract_task)
    communicate_task = build_communicate_task(
        communicator,
        analyze_task,
        document.meta.model_dump(),
    )

    crew = Crew(
        agents=[extractor, analyst, communicator],
        tasks=[extract_task, analyze_task, communicate_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    elapsed_ms = int((time.monotonic() - start_ms) * 1000)

    report = _parse_report(result, document.meta, elapsed_ms)
    return _post_process(report, document.raw_text)


def _parse_report(crew_output: object, doc_meta: DocMeta, processing_ms: int) -> Report:
    """Parse the Communicator's JSON output into a typed Report."""
    raw = str(crew_output)

    # Strip markdown code fences if present
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        data = json.loads(raw.strip())
    except json.JSONDecodeError:
        logger.error("Failed to parse crew output as JSON: %s", raw[:500])
        return Report(
            traffic_light=RiskLevel.RED,
            summary="Analysis could not be completed. Please try again.",
            findings=[],
            doc_meta=doc_meta,
            processing_ms=processing_ms,
        )

    findings = [Finding(**f) for f in data.get("findings", [])]
    traffic_light = RiskLevel(data.get("traffic_light", "red"))

    return Report(
        traffic_light=traffic_light,
        summary=data.get("summary", ""),
        findings=findings,
        doc_meta=doc_meta,
        processing_ms=processing_ms,
    )
