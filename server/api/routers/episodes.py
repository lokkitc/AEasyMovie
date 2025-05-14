from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import select
from typing import List

from api.dependencies.auth import get_current_user_from_token as get_current_user
from schemas.episodes import (
    EpisodeCreate,
    EpisodeList,
    EpisodeDetail,
    EpisodeDeleteResponse,
    EpisodeUpdate,
    EpisodeUpdateResponse
)
from schemas.users import UserRead
from db.session import get_db
from api.services.episode_service import (
    create_new_episode,
    delete_episode,
    get_episode,
    get_episodes_by_movie,
    update_episode,
    purchase_episode
)
from db.models.users import User
from db.models.movies import Movie
from db.models.episodes import Episode, PurchasedEpisode

episode_router = APIRouter()

@episode_router.get("/movie/{movie_id}", response_model=list[EpisodeList])
async def get_episodes_by_movie_router(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> list[EpisodeList]:
    """Получить список эпизодов фильма (без видео)"""
    return await get_episodes_by_movie(movie_id, session, current_user)

@episode_router.get("/{episode_id}", response_model=EpisodeDetail)
async def get_episode_router(
    episode_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> EpisodeDetail:
    """Получить детальную информацию об эпизоде (с видео)"""
    episode = await get_episode(episode_id, session, current_user)
    if not episode.has_access:
        raise HTTPException(
            status_code=403,
            detail="У вас нет доступа к этому эпизоду"
        )
    return episode

@episode_router.post("/", response_model=EpisodeList)
async def create_episode_router(
    movie_id: int = Form(...),
    title: str = Form(...),
    episode_number: int = Form(...),
    video: UploadFile = File(...),
    cost: float = Form(15.0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> EpisodeList:
    """Создать новый эпизод"""
    try:
        episode_data = EpisodeCreate(
            movie_id=movie_id,
            title=title,
            episode_number=episode_number,
            video=video,
            cost=cost
        )
        return await create_new_episode(episode_data, session, current_user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@episode_router.patch("/{episode_id}", response_model=EpisodeUpdateResponse)
async def update_episode_router(
    episode_id: int,
    body: EpisodeUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> EpisodeUpdateResponse:
    updated_episode_id = await update_episode(episode_id, body.model_dump(exclude_unset=True), session, current_user)
    return EpisodeUpdateResponse(updated_episode_id=updated_episode_id)

@episode_router.delete("/{episode_id}", response_model=EpisodeDeleteResponse)
async def delete_episode_router(
    episode_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> EpisodeDeleteResponse:
    deleted_episode_id = await delete_episode(episode_id, session, current_user)
    return EpisodeDeleteResponse(episode_id=deleted_episode_id)

@episode_router.post("/{episode_id}/purchase", response_model=EpisodeList)
async def purchase_episode_router(
    episode_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> EpisodeList:
    """Купить эпизод"""
    return await purchase_episode(episode_id, session, current_user) 