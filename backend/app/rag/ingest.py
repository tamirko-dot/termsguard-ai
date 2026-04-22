import json
import logging
from pathlib import Path

from app.rag.embedder import embed_texts
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by character count."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


def ingest_file(file_path: Path, source: str | None = None, metadata: dict | None = None) -> int:
    """Chunk, embed, and upsert a single text file into Supabase. Returns rows inserted."""
    text = file_path.read_text(encoding="utf-8")
    return ingest_text(text, source=source or str(file_path), metadata=metadata or {})


def ingest_text(text: str, source: str, metadata: dict | None = None) -> int:
    """Chunk, embed, and upsert raw text into Supabase. Returns rows inserted."""
    chunks = chunk_text(text)
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)
    supabase = get_supabase()

    rows = [
        {
            "content": chunk,
            "embedding": embedding,
            "source": source,
            "metadata": json.dumps(metadata or {}),
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    supabase.table("documents").insert(rows).execute()
    logger.info("Ingested %d chunks from '%s'", len(rows), source)
    return len(rows)


def ingest_directory(directory: Path, glob: str = "**/*.txt") -> int:
    """Ingest all matching files in a directory. Returns total rows inserted."""
    total = 0
    for file_path in sorted(directory.glob(glob)):
        total += ingest_file(file_path)
    return total
