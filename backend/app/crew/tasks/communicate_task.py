from crewai import Agent, Task


def build_communicate_task(agent: Agent, analyze_task: Task, doc_meta: dict) -> Task:
    return Task(
        description=(
            "You will receive a JSON array of AnalystFindings.\n\n"
            "Produce a final Report JSON object:\n"
            "  1. traffic_light: computed as follows:\n"
            "       - 'red'    if ANY finding has risk 'red'\n"
            "       - 'yellow' if NO red findings but ANY finding has risk 'yellow'\n"
            "       - 'green'  if ALL findings are green OR there are zero findings\n"
            "  2. summary: one short paragraph in plain English describing the overall risk.\n"
            "  3. findings: array where each item has:\n"
            "       - title: one-line plain-English title\n"
            "       - explanation: 1-2 sentences explaining the practical impact to the user\n"
            "       - risk: red | yellow | green\n"
            "       - source_quote: COPIED VERBATIM from the AnalystFinding — do not alter\n"
            "       - char_start: COPIED VERBATIM from the AnalystFinding\n"
            "       - char_end: COPIED VERBATIM from the AnalystFinding\n"
            "  4. doc_meta: " + str(doc_meta) + "\n\n"
            "Rules:\n"
            "  - Never add a finding the Analyst didn't produce.\n"
            "  - Never change source_quote, char_start, or char_end.\n"
            "  - Write for a general audience — no legalese.\n"
            "  - Output ONLY the JSON object. No prose before or after."
        ),
        expected_output=(
            "A single JSON Report object with fields: "
            "traffic_light, summary, findings[], doc_meta."
        ),
        agent=agent,
        context=[analyze_task],
    )
