from pydantic import BaseModel

class TagTextRequest(BaseModel):
    text: str

class TagTextResponse(BaseModel):
    message: str
    sentences_created: int
    tokens_created: int
