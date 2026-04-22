from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from app.rag.retriever import RetrievedChunk, retrieve


class RagSearchInput(BaseModel):
    query: str = Field(..., description="Search query to find relevant KB chunks")
    k: int = Field(5, description="Number of results to return")


class RagSearchTool(BaseTool):
    name: str = "rag_search_tool"
    description: str = (
        "Search the legal knowledge base (ToS;DR, GDPR, CCPA, sample ToS docs) "
        "for clauses and patterns similar to the given query. "
        "Returns the top-k most relevant text chunks with their sources."
    )
    args_schema: type[BaseModel] = RagSearchInput

    def _run(self, query: str, k: int = 5) -> str:
        chunks: list[RetrievedChunk] = retrieve(query, k=k)
        if not chunks:
            return "No relevant knowledge base entries found."
        lines = [
            f"[{i+1}] (source={c.source}, similarity={c.similarity:.3f})\n{c.content}"
            for i, c in enumerate(chunks)
        ]
        return "\n\n".join(lines)
