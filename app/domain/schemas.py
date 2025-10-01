from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    role: str = "annotator"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class PageMeta(BaseModel):
    current_page: int
    page_size: int
    total_pages: int
    total_items: int


class PaginatedUsersResponse(BaseModel):
    meta: PageMeta
    items: List[UserResponse]
