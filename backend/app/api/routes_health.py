from fastapi import APIRouter

router = APIRouter()

VERSION = "0.1.1"


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": VERSION}
