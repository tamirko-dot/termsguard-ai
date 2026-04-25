import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from crewai import Crew, Process
from langchain_core.messages import HumanMessage

from app.crew.agents.analyst import build_fast_analyst
from app.crew.agents.extractor import build_extractor
from app.crew.tasks.analyze_task import build_analyze_task_enriched
from app.crew.tasks.extract_task import build_extract_task
from app.crew.tools.clause_classifier_tool import ClauseClassifierTool
from app.crew.tools.rag_search_tool import RagSearchTool
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


def _enrich_clause(clause: dict) -> dict:
    """Run classifier (Python) + RAG (Supabase) for one clause — no LLM."""
    text = clause.get("text", "")
    classifier_result = ClauseClassifierTool()._run(clause_text=text)
    rag_result = RagSearchTool()._run(query=text[:500], k=3)
    return {**clause, "classifier": classifier_result, "rag": rag_result}


def _communicate_direct(analyst_output: str, doc_meta: dict) -> str:
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


def run_pipeline(document: Document) -> Report:
    start_ms = time.monotonic()

    # Phase 1 — Extract clauses (CrewAI extractor agent, gpt-4o-mini)
    extractor = build_extractor()
    extract_task = build_extract_task(extractor, document.raw_text)
    crew1 = Crew(
        agents=[extractor],
        tasks=[extract_task],
        process=Process.sequential,
        verbose=False,
    )
    extract_result = str(crew1.kickoff())

    # Parse clause list
    raw = extract_result
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        clauses = json.loads(raw.strip())
        if not isinstance(clauses, list):
            clauses = []
    except (json.JSONDecodeError, ValueError):
        logger.error("Extractor output is not valid JSON: %s", extract_result[:300])
        clauses = []

    # Phase 2 — Pre-fetch classifier + RAG for all clauses in parallel (no LLM)
    if clauses:
        with ThreadPoolExecutor(max_workers=10) as executor:
            enriched_clauses = list(executor.map(_enrich_clause, clauses))
    else:
        enriched_clauses = []

    # Phase 3 — Analyze all clauses in one shot (CrewAI analyst agent, gpt-4o-mini, no tools)
    analyst = build_fast_analyst()
    analyze_task = build_analyze_task_enriched(analyst, enriched_clauses)
    crew2 = Crew(
        agents=[analyst],
        tasks=[analyze_task],
        process=Process.sequential,
        verbose=False,
    )
    analyst_output = str(crew2.kickoff())

    # Phase 4 — Format into final report (direct LLM call, gpt-4o-mini)
    communicate_raw = _communicate_direct(analyst_output, document.meta.model_dump())

    elapsed_ms = int((time.monotonic() - start_ms) * 1000)
    report = _parse_report(communicate_raw, document.meta, elapsed_ms)
    return _post_process(report, document.raw_text)


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
