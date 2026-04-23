from crewai import Agent, Task


def build_analyze_task(agent: Agent, extract_task: Task) -> Task:
    return Task(
        description=(
            "You will receive a JSON array of clauses from the Extractor.\n\n"
            "For each clause:\n"
            "  1. Call clause_classifier_tool on the clause text.\n"
            "  2. BINDING RULE: If clause_classifier_tool returns 'red' or 'yellow', you MUST "
            "include that clause as a finding with that exact risk level. You may NOT downgrade "
            "a classifier result from red/yellow to green — the classifier is authoritative.\n"
            "  3. Call rag_search_tool(query=clause.text, k=5) to retrieve KB patterns for context.\n"
            "  4. Write a short English rationale (1-2 sentences).\n"
            "  5. Copy source_quote verbatim from clause.text.\n"
            "  6. Record char_start and char_end from the Extractor output.\n"
            "  7. List retrieved_refs (source filenames from the KB results).\n\n"
            "RISK CALIBRATION — follow these thresholds strictly:\n\n"
            "RED (serious harm to user):\n"
            "  - Selling, renting, or transferring personal data to third parties for profit\n"
            "  - Mandatory binding arbitration that waives class action rights\n"
            "  - Account termination at any time without notice or reason\n"
            "  - Retaining personal data indefinitely after account deletion\n"
            "  - Collecting biometric or sensitive health data\n"
            "  - Unilateral terms changes with zero notice (continued use = acceptance)\n\n"
            "YELLOW (moderate concern, user should be aware):\n"
            "  - Targeted advertising using personal behavioural data\n"
            "  - Broad content license (royalty-free, worldwide) even if user retains ownership\n"
            "  - Sharing data with analytics or service partners\n"
            "  - Auto-renewal billing with cancellation required to stop charges\n"
            "  - Data retention beyond 1 year after last use\n"
            "  - Using user content to train AI/ML models\n"
            "  - Terms changes with some notice (30 days or less)\n\n"
            "GREEN (user-friendly — do NOT flag as a risk):\n"
            "  - Minimal data collection (only what is needed)\n"
            "  - Explicit statement of no data selling\n"
            "  - User rights to export or permanently delete data\n"
            "  - Advance notice of policy changes (30+ days)\n"
            "  - Standard encryption or security practices\n"
            "  - Data deleted within 30 days of account closure\n\n"
            "CRITICAL RULES:\n"
            "  - Do NOT invent risks. Every finding must be grounded in an actual clause.\n"
            "  - If a document is genuinely user-protective with no RED or YELLOW clauses, "
            "produce zero findings or only GREEN findings.\n"
            "  - Drop standard boilerplate (contact info, definitions sections) unless they hide a real risk.\n"
            "  - 'We retain your data only for account duration and delete within 30 days of closure' "
            "is GREEN — do NOT flag it as a risk.\n"
            "  - 'We may change these terms at any time without prior notice' is RED — always flag it.\n"
            "  - 'Content used to train AI models' is YELLOW — always flag it.\n\n"
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
