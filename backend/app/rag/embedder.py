from app.services.llm_provider import get_embeddings


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return OpenAI embeddings for a batch of texts."""
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)


def embed_query(text: str) -> list[float]:
    """Return a single query embedding."""
    embeddings = get_embeddings()
    return embeddings.embed_query(text)
