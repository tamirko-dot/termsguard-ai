from unittest.mock import MagicMock, patch

from app.rag.ingest import chunk_text
from app.rag.retriever import RetrievedChunk, retrieve


def test_chunk_text_basic():
    text = "a" * 1200
    chunks = chunk_text(text, size=500, overlap=50)
    assert len(chunks) == 3
    assert all(len(c) <= 500 for c in chunks)


def test_chunk_text_overlap():
    text = "abcdefghij"
    chunks = chunk_text(text, size=6, overlap=2)
    # chunk 0: [0:6], chunk 1: [4:10]
    assert chunks[0] == "abcdef"
    assert chunks[1] == "efghij"


def test_chunk_text_empty():
    assert chunk_text("") == []


def test_retrieve_returns_chunks(monkeypatch):
    fake_response = MagicMock()
    fake_response.data = [
        {"content": "arbitration clause text", "source": "tosdr/sample.txt", "similarity": 0.91}
    ]

    fake_supabase = MagicMock()
    fake_supabase.rpc.return_value.execute.return_value = fake_response

    with patch("app.rag.retriever.get_supabase", return_value=fake_supabase), \
         patch("app.rag.retriever.embed_query", return_value=[0.1] * 1536):
        results = retrieve("arbitration", k=1)

    assert len(results) == 1
    assert isinstance(results[0], RetrievedChunk)
    assert results[0].similarity == 0.91
    assert results[0].source == "tosdr/sample.txt"


def test_retrieve_empty_result(monkeypatch):
    fake_response = MagicMock()
    fake_response.data = []

    fake_supabase = MagicMock()
    fake_supabase.rpc.return_value.execute.return_value = fake_response

    with patch("app.rag.retriever.get_supabase", return_value=fake_supabase), \
         patch("app.rag.retriever.embed_query", return_value=[0.0] * 1536):
        results = retrieve("nothing matches", k=5)

    assert results == []
