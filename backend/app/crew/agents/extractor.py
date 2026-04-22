from crewai import Agent

from app.services.llm_provider import get_primary_llm


def build_extractor() -> Agent:
    return Agent(
        role="Legal Document Structural Extractor",
        goal=(
            "Parse the raw ToS/Privacy Policy text and extract every distinct clause "
            "as a structured object with its verbatim text, a short topic label, "
            "and the exact character offsets (char_start, char_end) in the original document."
        ),
        backstory=(
            "You are a meticulous legal document parser. You never paraphrase — "
            "you copy clause text verbatim and record precise character positions "
            "so that downstream agents and the browser extension can highlight the "
            "exact source text. You split on paragraph breaks and numbered sections."
        ),
        llm=get_primary_llm(),
        verbose=True,
        allow_delegation=False,
    )
