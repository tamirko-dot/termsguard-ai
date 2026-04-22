from crewai.tools import BaseTool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from app.services.llm_provider import get_primary_llm


class PlainLanguageRewriterInput(BaseModel):
    legal_text: str = Field(..., description="Legal clause text to rewrite in plain English")


class PlainLanguageRewriterTool(BaseTool):
    name: str = "plain_language_rewriter_tool"
    description: str = (
        "Rewrite a dense legal clause into one or two plain-English sentences "
        "that a non-lawyer can understand in under 10 seconds. "
        "Do not add or remove facts — only simplify the language."
    )
    args_schema: type[BaseModel] = PlainLanguageRewriterInput

    def _run(self, legal_text: str) -> str:
        llm = get_primary_llm()
        prompt = (
            "Rewrite the following legal clause in plain English. "
            "Use at most two sentences. Do not add information not present in the original.\n\n"
            f"Clause:\n{legal_text}"
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
