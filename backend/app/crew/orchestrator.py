import json
import logging
import time

from crewai import Agent, Crew, Process, Task
from langchain_core.messages import HumanMessage

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

_TASK_TEMPLATE = """\
You are a privacy lawyer and legal document analyst.

Analyze the Terms of Service / Privacy Policy below.
Relevant legal knowledge base context is provided to guide your assessment.

LEGAL KNOWLEDGE BASE:
{rag_context}

DOCUMENT ({chars} chars):
{raw_text}

INSTRUCTIONS:
- Read the document and identify every clause that is RED or YELLOW risk.
- Skip standard/boilerplate clauses entirely — do not include them in output.
- For each risky clause, copy the exact verbatim text as source_quote.

RISK LEVELS:
RED — reasonable person would refuse to sign:
  • Selling or renting personal data to third parties
  • Mandatory binding arbitration / waiving class action rights
  • Retaining data indefinitely or after account deletion
  • Unilateral changes with zero notice
  • Irrevocable, perpetual content license

YELLOW — worth knowing:
  • Targeted / behavioural advertising
  • Sharing data with ad or analytics partners
  • Using content to train AI/ML models
  • Auto-renewal billing
  • Sole-discretion account termination
  • Data retention beyond 2 years
  • Terms changes with less than 14 days notice

GREEN — do NOT include in output:
  • Standard cookies or analytics for service improvement
  • 30+ days advance notice for changes
  • Minimal or purpose-limited data collection
  • Explicit no-sell / no-share statements
  • User rights to export or delete data
  • Standard security or encryption practices

OUTPUT: a single JSON object, no prose, no markdown fences:
{{
  "traffic_light": "red" | "yellow" | "green",
  "summary": "one short plain-English paragraph describing the overall risk level",
  "findings": [
    {{
      "title": "short plain-English title",
      "explanation": "1-2 sentences on the practical impact to the user",
      "risk": "red" | "yellow" | "green",
      "source_quote": "verbatim text copied from the document",
      "char_start": 0,
      "char_end": 0
    }}
  ]
}}

If no RED or YELLOW clauses exist, return traffic_light green and an empty findings array.\
"""


def _fetch_rag_context(raw_text: str) -> str:
    query = raw_text[:400]
    try:
        result = RagSearchTool()._run(query=query, k=4)
        lines = []
        for chunk in result.split("\n\n"):
            lines.append(chunk[:250])
        return "\n\n".join(lines)
    except Exception:
        return ""


def run_pipeline(document: Document) -> Report:
    start_ms = time.monotonic()

    rag_context = _fetch_rag_context(document.raw_text)

    truncated = document.raw_text[:10000]

    task_description = _TASK_TEMPLATE.format(
        rag_context=rag_context or "No context retrieved.",
        raw_text=truncated,
        chars=len(truncated),
    )

    agent = Agent(
        role="Privacy Policy Analyst",
        goal="Read a Terms of Service document and produce a structured risk report in JSON.",
        backstory=(
            "You are a privacy lawyer with expertise in GDPR, CCPA, and consumer rights. "
            "You identify clauses that could harm users and explain them in plain English."
        ),
        llm=get_fast_llm(),
        verbose=False,
        allow_delegation=False,
    )

    task = Task(
        description=task_description,
        expected_output="A single JSON object with traffic_light, summary, and findings array.",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

    result = str(crew.kickoff())
    elapsed_ms = int((time.monotonic() - start_ms) * 1000)

    report = _parse_report(result, document.meta, elapsed_ms)
    return _post_process(report)


def _post_process(report: Report) -> Report:
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
        logger.error("Failed to parse agent output as JSON: %s", raw[:500])
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
