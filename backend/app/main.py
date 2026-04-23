import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_analyze import router as analyze_router
from app.api.routes_health import router as health_router
from app.config import get_settings

settings = get_settings()

logging.basicConfig(level=settings.log_level.upper())

app = FastAPI(
    title="TermsGuard AI",
    description="Multi-agent RAG system for analyzing Terms of Service and Privacy Policies.",
    version="0.1.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analyze_router, prefix="/api/v1")
