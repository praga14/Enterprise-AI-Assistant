from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    content: str
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]