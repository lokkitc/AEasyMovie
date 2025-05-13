from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import UploadFile

class TunedModel(BaseModel):
    class Config:
        from_attributes = True

class EpisodeBase(BaseModel):
    episode_id: int
    movie_id: int
    title: str
    episode_number: int
    cost: float
    created_at: datetime
    updated_at: datetime
    has_access: bool

class EpisodeList(EpisodeBase):
    class Config:
        from_attributes = True

class EpisodeDetail(EpisodeBase):
    video_file: str

    class Config:
        from_attributes = True

class EpisodeCreate(BaseModel):
    movie_id: int
    title: str
    episode_number: int
    video: str
    cost: float = 15.0

class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    episode_number: Optional[int] = None
    cost: Optional[float] = None

class EpisodeUpdateResponse(BaseModel):
    updated_episode_id: int

class EpisodeDeleteResponse(BaseModel):
    episode_id: int 