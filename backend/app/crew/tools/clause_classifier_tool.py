from crewai.tools import BaseTool
from pydantic import BaseModel, Field

RED_KEYWORDS = [
    "arbitration", "waive", "class action", "irrevocable", "perpetual license",
    "sell your data", "third party advertising", "no refund", "auto-renew",
    "unilateral change", "without notice",
]
YELLOW_KEYWORDS = [
    "may share", "affiliated companies", "analytics", "cookies", "opt-out",
    "retain", "anonymized", "aggregated", "license to use",
]


class ClauseClassifierInput(BaseModel):
    clause_text: str = Field(..., description="The clause text to classify")


class ClauseClassifierTool(BaseTool):
    name: str = "clause_classifier_tool"
    description: str = (
        "Heuristically classify a ToS clause as red, yellow, or green "
        "based on known high-risk and medium-risk keyword patterns. "
        "Use as a fast pre-filter before deeper RAG analysis."
    )
    args_schema: type[BaseModel] = ClauseClassifierInput

    def _run(self, clause_text: str) -> str:
        lower = clause_text.lower()
        matched_red = [kw for kw in RED_KEYWORDS if kw in lower]
        matched_yellow = [kw for kw in YELLOW_KEYWORDS if kw in lower]

        if matched_red:
            return f"red — matched high-risk keywords: {matched_red}"
        if matched_yellow:
            return f"yellow — matched medium-risk keywords: {matched_yellow}"
        return "green — no high-risk or medium-risk keywords detected"
