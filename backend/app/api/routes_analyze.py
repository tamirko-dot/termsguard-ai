import asyncio
import logging
import uuid

from fastapi import APIRouter, HTTPException

from app.api.schemas import AnalyzeRequest, AnalyzeResponse
from app.crew.orchestrator import run_pipeline
from app.models.document import Document

logger = logging.getLogger(__name__)
router = APIRouter()

_jobs: dict[str, dict] = {}


@router.post("/analyze")
async def submit_analyze(request: AnalyzeRequest) -> dict:
    if not request.raw_text.strip():
        raise HTTPException(status_code=422, detail="raw_text must not be empty")

    document = Document(
        raw_text=request.raw_text,
        url=request.url,
        title=request.title,
    )

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending"}

    async def run():
        try:
            report = await asyncio.to_thread(run_pipeline, document)
            _jobs[job_id] = {
                "status": "done",
                "result": AnalyzeResponse(
                    traffic_light=report.traffic_light,
                    summary=report.summary,
                    findings=report.findings,
                    doc_meta=report.doc_meta,
                    processing_ms=report.processing_ms,
                ).model_dump(),
            }
        except Exception as exc:
            logger.exception("Pipeline failed: %s", exc)
            _jobs[job_id] = {"status": "error", "error": str(exc)}

    asyncio.create_task(run())
    return {"job_id": job_id}


@router.get("/analyze/{job_id}")
async def get_result(job_id: str) -> dict:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
