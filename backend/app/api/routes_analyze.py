import logging

from fastapi import APIRouter, HTTPException

from app.api.schemas import AnalyzeRequest, AnalyzeResponse
from app.crew.orchestrator import run_pipeline
from app.models.document import Document

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    if not request.raw_text.strip():
        raise HTTPException(status_code=422, detail="raw_text must not be empty")

    document = Document(
        raw_text=request.raw_text,
        url=request.url,
        title=request.title,
    )

    try:
        report = run_pipeline(document)
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        raise HTTPException(status_code=500, detail="Analysis pipeline failed") from exc

    return AnalyzeResponse(
        traffic_light=report.traffic_light,
        summary=report.summary,
        findings=report.findings,
        doc_meta=report.doc_meta,
        processing_ms=report.processing_ms,
    )
