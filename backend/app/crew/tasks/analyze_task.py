from crewai import Agent, Task


def build_analyze_task(agent: Agent, extract_task: Task) -> Task:
    return Task(
        description=(
            "You will receive a JSON array of clauses from the Extractor.\n\n"
            "For each clause:\n"
            "  1. Call clause_classifier_tool to get a fast heuristic risk estimate.\n"
            "  2. Call rag_search_tool(query=clause.text, k=5) to retrieve relevant KB patterns.\n"
            "  3. Based on both signals, assign risk: red | yellow | green.\n"
            "  4. Write a short English rationale (1-2 sentences).\n"
            "  5. Copy source_quote verbatim from clause.text (the exact substring that justifies the risk).\n"
            "  6. Record char_start and char_end from the Extractor output.\n"
            "  7. List retrieved_refs (source filenames from the KB results).\n\n"
            "Drop clauses that are clearly GREEN/standard (e.g. basic contact info sections) "
            "unless they contain a hidden risk.\n\n"
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
