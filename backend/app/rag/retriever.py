import logging

from app.config import get_settings
from app.rag.embedder import embed_query
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)


class RetrievedChunk:
    def __init__(self, content: str, source: str, similarity: float) -> None:
        self.content = content
        self.source = source
        self.similarity = similarity

    def __repr__(self) -> str:
        return f"RetrievedChunk(source={self.source!r}, similarity={self.similarity:.3f})"


def retrieve(query: str, k: int | None = None) -> list[RetrievedChunk]:
    """Embed query and return the top-k most similar chunks from Supabase."""
    settings = get_settings()
    top_k = k or settings.rag_top_k
    query_embedding = embed_query(query)

    supabase = get_supabase()
    response = supabase.rpc(
        "match_documents",
        {"query_embedding": query_embedding, "match_count": top_k},
    ).execute()

    results: list[RetrievedChunk] = []
    for row in response.data or []:
        results.append(
            RetrievedChunk(
                content=row["content"],
                source=row.get("source", ""),
                similarity=row.get("similarity", 0.0),
            )
        )

    logger.debug("Retrieved %d chunks for query: %s", len(results), query[:60])
    return results
