from pydantic import BaseModel, Field

from app.models.document import DocMeta
from app.models.finding import Finding, RiskLevel


class Report(BaseModel):
    traffic_light: RiskLevel = Field(..., description="Worst severity found across all findings")
    summary: str = Field(..., description="One-paragraph plain-English summary for non-lawyers")
    findings: list[Finding]
    doc_meta: DocMeta
    processing_ms: int = Field(..., description="End-to-end pipeline latency in milliseconds")
