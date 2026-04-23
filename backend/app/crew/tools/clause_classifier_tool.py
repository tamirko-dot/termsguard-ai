from crewai.tools import BaseTool
from pydantic import BaseModel, Field

RED_KEYWORDS = [
    # Waiving legal rights
    "arbitration", "waive", "class action", "irrevocable perpetual",
    # Selling / renting user data
    "sell your data", "sell your personal", "rent your data",
    # No refunds
    "no refund",
    # Changing terms with zero notice
    "without prior notice", "without notice",
    # Keeping data forever / after deletion
    "retain your data indefinitely", "retain indefinitely",
    "after account deletion",
]
YELLOW_KEYWORDS = [
    # Sharing data with partners
    "may share", "affiliated companies", "third-party advertisers",
    "third party advertising", "data broker",
    # Behavioural advertising
    "targeted advertising", "personalised advertising", "personalized advertising",
    # AI training
    "train our ai", "train ai", "ai model", "machine learning model",
    "used to train", "improve our model",
    # Broad content licensing
    "license to use",
    # Billing / subscription
    "auto-renew", "automatically renew",
    # Broad discretion / termination without cause
    "at our sole discretion", "terminate your account at any time",
    # Long data retention
    "retain your data for", "store your data for",
    # Opt-out required (default-on)
    "opt-out",
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
