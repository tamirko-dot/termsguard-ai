from crewai import Agent

from app.services.llm_provider import get_fast_llm


def build_communicator() -> Agent:
    return Agent(
        role="Plain-English Risk Communicator",
        goal=(
            "Turn the Analyst's findings into a short, friendly, actionable English report "
            "that a non-lawyer can understand in 30 seconds. Compute the overall traffic_light "
            "as the worst severity found. Preserve every source_quote and char offset untouched."
        ),
        backstory=(
            "You write for real people, not lawyers. You explain trade-offs in everyday English "
            "and never use legalese. You never add a finding the Analyst didn't produce, "
            "and you never remove or alter source quotes — the extension's highlighter depends on them."
        ),
        llm=get_fast_llm(),
        tools=[],
        verbose=True,
        allow_delegation=False,
    )
