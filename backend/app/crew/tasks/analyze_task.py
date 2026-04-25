import json

from crewai import Agent, Task


def build_analyze_task(agent: Agent, extract_task: Task) -> Task:
    return Task(
        description=(
            "You will receive a JSON array of clauses from the Extractor.\n\n"
            "For each clause:\n"
            "  1. Call clause_classifier_tool on the clause text for a quick signal.\n"
            "  2. The classifier is a HINT only — use your legal judgment to set the final risk. "
            "You CAN downgrade a classifier result if the full context makes it safe "
            "(e.g. 'without notice' in a refund policy, not a terms-change clause).\n"
            "  3. Call rag_search_tool(query=clause.text, k=5) to retrieve KB patterns for context.\n"
            "  4. Write a short English rationale (1-2 sentences).\n"
            "  5. Copy source_quote verbatim from clause.text.\n"
            "  6. Record char_start and char_end from the Extractor output.\n"
            "  7. List retrieved_refs (source filenames from the KB results).\n\n"
            "RISK CALIBRATION — the standard: would a reasonable person refuse to sign this?\n\n"
            "RED (clear user harm — reasonable person would refuse to sign):\n"
            "  - Selling or renting personal data to third parties for profit\n"
            "  - Mandatory binding arbitration waiving class action rights\n"
            "  - Retaining personal data indefinitely or after account deletion\n"
            "  - Unilateral terms changes with ZERO notice ('at any time without notice')\n"
            "  - Irrevocable, perpetual content license stripping user ownership\n\n"
            "YELLOW (worth knowing, but not a dealbreaker):\n"
            "  - Targeted / behavioural advertising using personal data\n"
            "  - Sharing data with third-party analytics or advertising partners\n"
            "  - Using user content to train AI/ML models\n"
            "  - Auto-renewal billing that requires active cancellation\n"
            "  - Broad 'sole discretion' termination without cause\n"
            "  - Data retention beyond 2 years after last use\n"
            "  - Terms changes with short notice (under 14 days)\n\n"
            "GREEN (normal — do NOT flag):\n"
            "  - Standard cookie / analytics for service improvement\n"
            "  - Terms changes with 30+ days advance notice\n"
            "  - Minimal or purpose-limited data collection\n"
            "  - Explicit no-sell / no-share statements\n"
            "  - User rights to export or delete data\n"
            "  - Standard encryption or security practices\n"
            "  - Data deleted within 30 days of account closure\n"
            "  - Account termination for ToS violations (legitimate enforcement)\n\n"
            "CRITICAL RULES:\n"
            "  - Do NOT invent risks. Every finding must be grounded in an actual clause.\n"
            "  - If a document is genuinely user-protective, produce zero findings.\n"
            "  - Drop boilerplate (definitions, contact info) unless it hides a real risk.\n"
            "  - 'We use cookies to improve your experience' → GREEN, do not flag.\n"
            "  - 'We will notify you 30 days before any changes' → GREEN, do not flag.\n"
            "  - 'We may change terms at any time without prior notice' → RED, always flag.\n"
            "  - 'Content used to train AI models' → YELLOW, always flag.\n\n"
            "Output ONLY a JSON array of findings. No prose.\n"
            "Each finding: { clause_id, topic, risk, rationale, source_quote, char_start, char_end, retrieved_refs }"
        ),
        expected_output=(
            "A JSON array of AnalystFinding objects with fields: "
            "clause_id, topic, risk, rationale, source_quote, char_start, char_end, retrieved_refs."
        ),
        agent=agent,
        context=[extract_task],
    )


def build_analyze_task_enriched(agent: Agent, enriched_clauses: list[dict]) -> Task:
    """Single-shot analysis task with classifier + RAG context pre-injected — no tool calls needed."""
    clauses_block = json.dumps(
        [
            {
                "clause_id": c.get("clause_id"),
                "topic": c.get("topic"),
                "text": c.get("text"),
                "char_start": c.get("char_start", 0),
                "char_end": c.get("char_end", 0),
                "classifier_hint": c.get("classifier", ""),
                "kb_context": c.get("rag", ""),
            }
            for c in enriched_clauses
        ],
        indent=2,
    )

    return Task(
        description=(
            "All clauses have been pre-processed with classifier hints and knowledge base context.\n\n"
            "For each clause below, use the classifier_hint and kb_context already provided — "
            "DO NOT call any tools.\n\n"
            "RISK CALIBRATION — the standard: would a reasonable person refuse to sign this?\n\n"
            "RED (clear user harm):\n"
            "  - Selling or renting personal data to third parties for profit\n"
            "  - Mandatory binding arbitration waiving class action rights\n"
            "  - Retaining personal data indefinitely or after account deletion\n"
            "  - Unilateral terms changes with ZERO notice\n"
            "  - Irrevocable, perpetual content license stripping user ownership\n\n"
            "YELLOW (worth knowing):\n"
            "  - Targeted / behavioural advertising using personal data\n"
            "  - Sharing data with third-party analytics or advertising partners\n"
            "  - Using user content to train AI/ML models\n"
            "  - Auto-renewal billing\n"
            "  - Broad sole-discretion termination\n"
            "  - Data retention beyond 2 years\n"
            "  - Terms changes with under 14 days notice\n\n"
            "GREEN (do NOT flag):\n"
            "  - Standard cookies / analytics\n"
            "  - 30+ days notice for changes\n"
            "  - Minimal data collection\n"
            "  - Explicit no-sell statements\n"
            "  - User data rights\n"
            "  - Standard security practices\n"
            "  - Data deleted within 30 days of account closure\n\n"
            "CRITICAL RULES:\n"
            "  - Do NOT invent risks. Every finding must be grounded in an actual clause.\n"
            "  - Drop GREEN and boilerplate clauses entirely.\n"
            "  - Output ONLY a JSON array. No prose.\n"
            "  - Each finding: { clause_id, topic, risk, rationale, source_quote, char_start, char_end, retrieved_refs }\n\n"
            f"Clauses to analyze:\n{clauses_block}"
        ),
        expected_output=(
            "A JSON array of AnalystFinding objects with fields: "
            "clause_id, topic, risk, rationale, source_quote, char_start, char_end, retrieved_refs."
        ),
        agent=agent,
    )
