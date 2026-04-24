from crewai import Agent, Task


def build_extract_task(agent: Agent, raw_text: str) -> Task:
    return Task(
        description=(
            f"Parse the following Terms of Service / Privacy Policy text.\n\n"
            f"For each distinct clause or section, output a JSON array where every item has:\n"
            f"  - clause_id: sequential string (\"c1\", \"c2\", ...)\n"
            f"  - topic: short label (e.g. \"Data Sharing\", \"Arbitration\")\n"
            f"  - text: verbatim clause text copied exactly from the source\n"
            f"  - char_start: integer index where the clause starts in the original text\n"
            f"  - char_end: integer index where it ends\n\n"
            f"Output ONLY the JSON array. No prose before or after.\n\n"
            f"Document (first 15000 chars shown):\n{raw_text[:15000]}"
        ),
        expected_output=(
            "A JSON array of clause objects with fields: "
            "clause_id, topic, text, char_start, char_end."
        ),
        agent=agent,
    )
