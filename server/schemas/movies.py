from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from db.models.movies import MovieAccessLevel

class TunedModel(BaseModel):
    class Config:
        from_attributes = True

class MovieRead(TunedModel):
    movie_id: int
    title: str
    original_title: str
    description: str
    poster: str
    backdrop: str
    release_date: datetime
    duration: int
    rating: float
    director: str
    genres: List[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    movie_url: Optional[str] = None

class MovieCreate(BaseModel):
    title: str
    original_title: str
    description: str
    poster: Optional[str] = None
    backdrop: Optional[str] = None
    release_date: datetime
    duration: int
    director: str
    genres: List[str]

    @field_validator("duration")
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v

    @field_validator("release_date")
    def validate_release_date(cls, v):
        if v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v

class MovieUpdateRequest(BaseModel):
    title: Optional[str] = None
    original_title: Optional[str] = None
    description: Optional[str] = None
    poster: Optional[str] = None
    backdrop: Optional[str] = None
    release_date: Optional[datetime] = None
    duration: Optional[int] = None
    director: Optional[str] = None
    genres: Optional[List[str]] = None
    movie_url: Optional[str] = None

    class Config:
        extra = "forbid"
        validate_assignment = True

class MovieDeleteResponse(BaseModel):
    movie_id: int

class MovieUpdateResponse(BaseModel):
    updated_movie_id: int

class MovieAccessLevelUpdate(BaseModel):
    access_level: MovieAccessLevel

class MovieAccessLevelResponse(BaseModel):
    movie_id: int
    access_level: MovieAccessLevel 