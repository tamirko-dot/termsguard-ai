import json
import logging
import time

from crewai import Crew, Process

from app.crew.agents.analyst import build_analyst
from app.crew.agents.communicator import build_communicator
from app.crew.agents.extractor import build_extractor
from app.crew.tasks.analyze_task import build_analyze_task
from app.crew.tasks.communicate_task import build_communicate_task
from app.crew.tasks.extract_task import build_extract_task
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


def _post_process(report: Report, raw_text: str) -> Report:
    """Apply deterministic corrections on top of LLM output."""

    # ── Step 1: remove false-positive findings ────────────────────────────
    findings = [
        f for f in report.findings
        if not any(gi in f.source_quote.lower() for gi in _GREEN_INDICATORS)
    ]

    # ── Step 2: recompute traffic_light from final findings ───────────────
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
