from fastapi import HTTPException, UploadFile
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import shutil
from schemas.episodes import EpisodeCreate, EpisodeList, EpisodeDetail
from db.dals.episode_dal import EpisodeDAL
from db.models.episodes import Episode, PurchasedEpisode
from db.models.movies import Movie
from db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from db.dals.user_dal import UserDAL
from sqlalchemy import select, and_

async def save_video_file(file: UploadFile, movie_id: int) -> str:
    """Сохраняет видеофайл и возвращает путь к нему"""
    # Создаем директорию для фильма, если она не существует
    movie_dir = f"server/media/videos/movie_{movie_id}"
    os.makedirs(movie_dir, exist_ok=True)
    
    # Генерируем уникальное имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"episode_{timestamp}{file_extension}"
    file_path = os.path.join(movie_dir, new_filename)
    
    # Сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")
    finally:
        file.file.close()
    
    return f"/media/videos/movie_{movie_id}/{new_filename}"

async def check_episode_access(user: User, episode_id: int, session: AsyncSession) -> bool:
    """Проверяет доступ пользователя к эпизоду"""
    if user.is_premium_active():
        return True
        
        purchased = await session.execute(
            select(PurchasedEpisode).where(
                and_(
                PurchasedEpisode.user_id == user.user_id,
                    PurchasedEpisode.episode_id == episode_id
                )
            )
        )
    return purchased.scalar_one_or_none() is not None

async def create_new_episode(body: EpisodeCreate, session: AsyncSession, current_user: User) -> EpisodeList:
    episode_dal = EpisodeDAL(session)
    
    # Проверяем существование фильма
    movie = await session.get(Movie, body.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Фильм с id {body.movie_id} не найден")
        
    # Проверяем права доступа
    if not movie.can_modify(current_user):
        raise HTTPException(status_code=403, detail="У вас нет прав на добавление эпизодов к этому фильму")
    
    # Сохраняем видеофайл
    video_path = await save_video_file(body.video, body.movie_id)
        
    new_episode = await episode_dal.create_episode(
        movie_id=body.movie_id,
        title=body.title,
        video_file=video_path,
        episode_number=body.episode_number,
        cost=body.cost
    )
    
    has_access = await check_episode_access(current_user, new_episode.episode_id, session)
    
    return EpisodeList(
        episode_id=new_episode.episode_id,
        movie_id=new_episode.movie_id,
        title=new_episode.title,
        episode_number=new_episode.episode_number,
        cost=new_episode.cost,
        created_at=new_episode.created_at,
        updated_at=new_episode.updated_at,
        has_access=has_access
    )

async def get_episode(episode_id: int, session: AsyncSession, current_user: User) -> EpisodeDetail:
    try:
        episode_dal = EpisodeDAL(session)
        episode = await episode_dal.get_episode(episode_id=episode_id)
        
        if episode is None:
            raise HTTPException(
                status_code=404,
                detail=f"Эпизод с id {episode_id} не найден"
            )
            
        # Проверяем доступ к фильму
        movie = await session.get(Movie, episode.movie_id)
        if not movie.can_access(current_user):
            raise HTTPException(
                status_code=403,
                detail="У вас нет доступа к этому эпизоду"
            )
            
        has_access = await check_episode_access(current_user, episode_id, session)
            
        return EpisodeDetail(
            episode_id=episode.episode_id,
            movie_id=episode.movie_id,
            title=episode.title,
            video_file=episode.video_file,
            episode_number=episode.episode_number,
            cost=episode.cost,
            created_at=episode.created_at,
            updated_at=episode.updated_at,
            has_access=has_access
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

async def get_episodes_by_movie(movie_id: int, session: AsyncSession, current_user: User) -> List[EpisodeList]:
    try:
        # Проверяем существование фильма и доступ
        movie = await session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail=f"Фильм с id {movie_id} не найден")
            
        if not movie.can_access(current_user):
            raise HTTPException(status_code=403, detail="У вас нет доступа к этому фильму")
            
        episode_dal = EpisodeDAL(session)
        episodes = await episode_dal.get_episodes_by_movie(movie_id=movie_id)
        
        result = []
        for episode in episodes:
            has_access = await check_episode_access(current_user, episode.episode_id, session)
            result.append(EpisodeList(
            episode_id=episode.episode_id,
            movie_id=episode.movie_id,
            title=episode.title,
            episode_number=episode.episode_number,
            cost=episode.cost,
            created_at=episode.created_at,
                updated_at=episode.updated_at,
                has_access=has_access
            ))
        
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

async def update_episode(episode_id: int, updated_episode_params: dict, session: AsyncSession, current_user: User) -> Optional[int]:
        episode_dal = EpisodeDAL(session)
        episode = await episode_dal.get_episode(episode_id=episode_id)
        
        if not episode:
            raise HTTPException(status_code=404, detail=f"Эпизод с id {episode_id} не найден")
            
        # Проверяем права доступа
        movie = await session.get(Movie, episode.movie_id)
        if not movie.can_modify(current_user):
            raise HTTPException(status_code=403, detail="У вас нет прав на изменение этого эпизода")
            
        await episode_dal.update_episode(
            episode_id=episode_id,
            **updated_episode_params,
            updated_at=datetime.now()
        )
        return episode_id

async def delete_episode(episode_id: int, session: AsyncSession, current_user: User) -> Optional[int]:
        episode_dal = EpisodeDAL(session)
        episode = await episode_dal.get_episode(episode_id=episode_id)
        
        if not episode:
            raise HTTPException(status_code=404, detail=f"Эпизод с id {episode_id} не найден")
            
        # Проверяем права доступа
        movie = await session.get(Movie, episode.movie_id)
        if not movie.can_modify(current_user):
            raise HTTPException(status_code=403, detail="У вас нет прав на удаление этого эпизода")
            
        return await episode_dal.delete_episode(episode_id=episode_id)

async def purchase_episode(episode_id: int, session: AsyncSession, current_user: User) -> EpisodeList:
    """Покупка эпизода"""
    episode = await session.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Эпизод не найден")
    
    # Проверяем, не куплен ли уже эпизод
    if await check_episode_access(current_user, episode_id, session):
        raise HTTPException(status_code=400, detail="У вас уже есть доступ к этому эпизоду")
        
    # Проверяем, достаточно ли денег
    can_watch, message = current_user.can_watch_episode(episode.cost)
    if not can_watch:
        raise HTTPException(status_code=403, detail=message)
        
    # Списываем деньги
    current_user.money -= episode.cost
    
    # Создаем запись о покупке
    purchased_episode = PurchasedEpisode(
        user_id=current_user.user_id,
        episode_id=episode_id,
        cost=episode.cost
    )
    session.add(purchased_episode)
    
    await session.commit()
    await session.refresh(current_user)
    
    # Возвращаем обновленную информацию об эпизоде
    has_access = await check_episode_access(current_user, episode_id, session)
    return EpisodeList(
        episode_id=episode.episode_id,
        movie_id=episode.movie_id,
        title=episode.title,
        episode_number=episode.episode_number,
        cost=episode.cost,
        created_at=episode.created_at,
        updated_at=episode.updated_at,
        has_access=has_access
    ) 