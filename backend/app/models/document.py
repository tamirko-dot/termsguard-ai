from pydantic import BaseModel, Field


class DocMeta(BaseModel):
    url: str | None = None
    length: int
    lang: str = "en"


class Document(BaseModel):
    raw_text: str = Field(..., description="Full plain text of the ToS/Privacy Policy page")
    url: str | None = Field(None, description="Source URL of the document")
    title: str | None = Field(None, description="Page title if available")

    @property
    def meta(self) -> DocMeta:
        return DocMeta(url=self.url, length=len(self.raw_text))
