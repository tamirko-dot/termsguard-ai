import json
import logging
import time

from crewai import Crew, Process
from langchain_core.messages import HumanMessage

from app.crew.agents.analyst import build_analyst
from app.crew.agents.extractor import build_extractor
from app.crew.tasks.analyze_task import build_analyze_task
from app.crew.tasks.extract_task import build_extract_task
from app.models.document import DocMeta, Document
from app.models.finding import Finding, RiskLevel
from app.models.report import Report
from app.services.llm_provider import get_fast_llm

_GREEN_INDICATORS = [
    "do not sell", "will not sell", "not sell", "never sell",
    "delete within 30", "delete it within", "deleted within",
    "permanently delete", "only for the duration of your account",
    "60 days in advance", "90 days in advance",
    "minimum data necessary", "only the minimum",
]

logger = logging.getLogger(__name__)


def _communicate_direct(analyst_output: str, doc_meta: dict) -> str:
    """Single direct LLM call — no CrewAI agent loop."""
    prompt = (
        "You will receive a JSON array of AnalystFindings.\n\n"
        "Produce a final Report JSON object:\n"
        "  1. traffic_light: 'red' if ANY finding has risk 'red'; "
        "'yellow' if no red but ANY yellow; 'green' if all green or zero findings.\n"
        "  2. summary: one short paragraph in plain English describing the overall risk.\n"
        "  3. findings: array where each item has:\n"
        "       - title: one-line plain-English title\n"
        "       - explanation: 1-2 sentences explaining the practical impact to the user\n"
        "       - risk: red | yellow | green\n"
        "       - source_quote: COPIED VERBATIM from the AnalystFinding\n"
        "       - char_start: COPIED VERBATIM from the AnalystFinding\n"
        "       - char_end: COPIED VERBATIM from the AnalystFinding\n"
        f"  4. doc_meta: {doc_meta}\n\n"
        "Rules: never add findings the Analyst didn't produce; never alter source_quote or char offsets; "
        "write for a general audience — no legalese; output ONLY the JSON object.\n\n"
        f"Analyst findings:\n{analyst_output}"
    )
    llm = get_fast_llm()
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def _post_process(report: Report, raw_text: str) -> Report:
    findings = [
        f for f in report.findings
        if not any(gi in f.source_quote.lower() for gi in _GREEN_INDICATORS)
    ]
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


def run_pipeline(document: Document) -> Report:
    start_ms = time.monotonic()

    extractor = build_extractor()
    analyst = build_analyst()

    extract_task = build_extract_task(extractor, document.raw_text)
    analyze_task = build_analyze_task(analyst, extract_task)

    crew = Crew(
        agents=[extractor, analyst],
        tasks=[extract_task, analyze_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    analyst_output = str(result)

    communicate_raw = _communicate_direct(analyst_output, document.meta.model_dump())

    elapsed_ms = int((time.monotonic() - start_ms) * 1000)
    report = _parse_report(communicate_raw, document.meta, elapsed_ms)
    return _post_process(report, document.raw_text)


def _parse_report(raw: str, doc_meta: DocMeta, processing_ms: int) -> Report:
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        data = json.loads(raw.strip())
    except json.JSONDecodeError:
        logger.error("Failed to parse communicate output as JSON: %s", raw[:500])
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
