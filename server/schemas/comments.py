from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from schemas.users import UserRead

class TunedModel(BaseModel):
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    rating: int
    movie_id: int
    parent_comment_id: Optional[int] = None

    @field_validator("rating")
    def validate_rating(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Rating must be between 1 and 10")
        return v

    @field_validator("content")
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Content cannot be empty")
        return v

class CommentCreate(CommentBase):
    pass

class CommentRead(TunedModel):
    comment_id: int
    user_id: int
    movie_id: int
    content: str
    rating: int
    parent_comment_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    user: UserRead

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    rating: Optional[int] = None

    class Config:
        extra = "forbid"
        validate_assignment = True

class CommentDeleteResponse(BaseModel):
    comment_id: int

class CommentUpdateResponse(BaseModel):
    updated_comment_id: int 