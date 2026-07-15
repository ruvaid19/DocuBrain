from pydantic import BaseModel
from typing import List

class SourceCitation(BaseModel):
    document_id: str
    page_number: int
    text_snippet: str

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
