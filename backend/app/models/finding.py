from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


class AnalystFinding(BaseModel):
    """Raw finding produced by the Analyst agent — includes internal KB refs."""

    clause_id: str
    topic: str
    risk: RiskLevel
    rationale: str
    source_quote: str = Field(..., description="Verbatim substring copied from the input text")
    char_start: int
    char_end: int
    retrieved_refs: list[str] = Field(default_factory=list, description="KB document IDs used")


class Finding(BaseModel):
    """Public finding included in the final Report — user-facing fields only."""

    title: str
    explanation: str
    risk: RiskLevel
    source_quote: str = Field(..., description="Verbatim substring for in-page highlighting")
    char_start: int
    char_end: int
