from crewai import Agent

from app.crew.tools.clause_classifier_tool import ClauseClassifierTool
from app.crew.tools.rag_search_tool import RagSearchTool
from app.services.llm_provider import get_primary_llm


def build_analyst() -> Agent:
    return Agent(
        role="Legal Risk Analyst",
        goal=(
            "For each extracted clause, search the legal knowledge base, classify the risk "
            "as red / yellow / green, and produce a structured finding with a rationale "
            "and the verbatim source_quote + char offsets. Drop clearly green/standard clauses."
        ),
        backstory=(
            "You are a privacy lawyer with deep knowledge of GDPR, CCPA, and ToS;DR ratings. "
            "You never invent findings — every risk assessment must be grounded in a retrieved "
            "KB reference or an explicit clause match. You are concise and precise."
        ),
        llm=get_primary_llm(),
        tools=[RagSearchTool(), ClauseClassifierTool()],
        verbose=True,
        allow_delegation=False,
    )
