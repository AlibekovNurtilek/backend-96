from pydantic import BaseModel
from typing import List, Optional


class TagTextRequest(BaseModel):
    text: str


class TagTextResponse(BaseModel):
    message: str
    sentences_created: int
    tokens_created: int


class TokenResponse(BaseModel):
    id: int
    token_index: str
    form: str
    lemma: str
    pos: str
    xpos: str
    feats: Optional[dict] = None

    class Config:
        from_attributes = True


class SentenceResponse(BaseModel):
    id: int
    text: str
    is_corrected: int

    class Config:
        from_attributes = True


class SentenceWithTokensResponse(SentenceResponse):
    tokens: List[TokenResponse]


class PageMeta(BaseModel):
    current_page: int
    page_size: int
    total_pages: int
    total_items: int


class PaginatedSentencesResponse(BaseModel):
    meta: PageMeta
    items: List[SentenceResponse]


class TokenUpdate(BaseModel):
    id: int
    token_index: Optional[str] = None
    form: Optional[str] = None
    lemma: Optional[str] = None
    pos: Optional[str] = None
    xpos: Optional[str] = None
    feats: Optional[dict] = None


class UpdateSentenceRequest(BaseModel):
    sentence_text: Optional[str] = None
    is_corrected: Optional[int] = None
    tokens: Optional[List[TokenUpdate]] = None
