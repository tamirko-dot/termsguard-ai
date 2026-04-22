from pydantic import BaseModel, Field

from app.models.document import DocMeta
from app.models.finding import Finding, RiskLevel


class AnalyzeRequest(BaseModel):
    raw_text: str = Field(..., description="Full plain text of the ToS/Privacy Policy")
    url: str | None = Field(None, description="Source URL")
    title: str | None = Field(None, description="Page title")


class AnalyzeResponse(BaseModel):
    traffic_light: RiskLevel
    summary: str
    findings: list[Finding]
    doc_meta: DocMeta
    processing_ms: int
