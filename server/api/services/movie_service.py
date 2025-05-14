from fastapi import HTTPException
from typing import Union, List
from datetime import datetime
from schemas.movies import MovieCreate, MovieRead
from db.dals.movie_dal import MovieDAL
from db.models.movies import Movie, MovieAccessLevel
from db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession

async def create_new_movie(body: MovieCreate, session, current_user: User) -> MovieRead:
        movie_dal = MovieDAL(session)
        new_movie = await movie_dal.create_movie(
            title=body.title,
            original_title=body.original_title,
            description=body.description,
            poster=body.poster or Movie.DEFAULT_POSTER,
            backdrop=body.backdrop or Movie.DEFAULT_BACKDROP,
            release_date=body.release_date,
            duration=body.duration,
            director=body.director,
            genres=",".join(body.genres),
            owner_id=current_user.user_id,
        )
        return MovieRead(
            movie_id=new_movie.movie_id,
            title=new_movie.title,
            original_title=new_movie.original_title,
            description=new_movie.description,
            poster=new_movie.poster,
            backdrop=new_movie.backdrop,
            release_date=new_movie.release_date,
            duration=new_movie.duration,
            rating=new_movie.rating,
            director=new_movie.director,
            genres=new_movie.genres.split(",") if new_movie.genres else [],
            created_at=new_movie.created_at,
            updated_at=new_movie.updated_at,
            is_active=new_movie.is_active,
            movie_url=new_movie.movie_url,
        )

async def delete_movie(movie_id: int, session) -> Union[int, None]:
        movie_dal = MovieDAL(session)
        deleted_movie_id = await movie_dal.delete_movie(movie_id=movie_id)
        return deleted_movie_id

async def get_movie(movie_id: int, session) -> Union[MovieRead, None]:
    try:
        movie_dal = MovieDAL(session)
        movie = await movie_dal.get_movie(movie_id=movie_id)
        
        if movie is None:
            raise HTTPException(
                status_code=404,
                detail=f"Фильм с id {movie_id} не найден"
            )
        
        if not movie.is_active:
            raise HTTPException(
                status_code=404,
                detail=f"Фильм с id {movie_id} неактивен"
            )
            
        return MovieRead(
            movie_id=movie.movie_id,
            title=movie.title,
            original_title=movie.original_title,
            description=movie.description,
            poster=movie.poster,
            backdrop=movie.backdrop,
            release_date=movie.release_date,
            duration=movie.duration,
            rating=movie.rating,
            director=movie.director,
            genres=movie.genres.split(",") if movie.genres else [],
            created_at=movie.created_at,
            updated_at=movie.updated_at,
            is_active=movie.is_active,
            movie_url=movie.movie_url,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_movie: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

async def get_movies(session) -> List[MovieRead]:
    movie_dal = MovieDAL(session)
    movies = await movie_dal.get_movies()
    return [MovieRead(
        movie_id=movie.movie_id,
        title=movie.title,
        original_title=movie.original_title,
        description=movie.description,
        poster=movie.poster,
        backdrop=movie.backdrop,
        release_date=movie.release_date,
        duration=movie.duration,
        rating=movie.rating,
        director=movie.director,
        genres=movie.genres.split(",") if movie.genres else [],
        created_at=movie.created_at,
        updated_at=movie.updated_at,
            is_active=movie.is_active,
            movie_url=movie.movie_url,
        ) for movie in movies]

async def update_movie(updated_movie_params: dict, movie_id: int, session) -> Union[int, None]:
    movie_dal = MovieDAL(session)
    if "genres" in updated_movie_params:
        updated_movie_params["genres"] = ",".join(updated_movie_params["genres"])
    if "release_date" in updated_movie_params and updated_movie_params["release_date"].tzinfo is not None:
        updated_movie_params["release_date"] = updated_movie_params["release_date"].replace(tzinfo=None)
    result = await movie_dal.update_movie(
        movie_id=movie_id,
        **updated_movie_params,
        updated_at=datetime.now()
    )
    return movie_id

async def check_movie_access(movie_id: int, user: User, session: AsyncSession) -> bool:
    """
    Проверяет доступ пользователя к фильму
    """
    try:
        movie_dal = MovieDAL(session)
        movie = await movie_dal.get_movie(movie_id=movie_id)
        
        if not movie:
            raise HTTPException(status_code=404, detail=f"Фильм с id {movie_id} не найден")
        
        if not movie.is_active:
            raise HTTPException(status_code=404, detail=f"Фильм с id {movie_id} неактивен")
            
        return movie.can_access(user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

async def check_movie_modify(movie_id: int, user: User, session: AsyncSession) -> bool:
    """
    Проверяет право пользователя на модификацию фильма
    """
    movie_dal = MovieDAL(session)
    movie = await movie_dal.get_movie(movie_id=movie_id)
        
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
            
    return movie.can_modify(user)

async def check_movie_delete(movie_id: int, user: User, session: AsyncSession) -> bool:
    """
    Проверяет право пользователя на удаление фильма
    """
    movie_dal = MovieDAL(session)
    movie = await movie_dal.get_movie(movie_id=movie_id)
        
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
            
    return movie.can_delete(user)

async def update_movie_access_level(movie_id: int, access_level: MovieAccessLevel, user: User, session: AsyncSession) -> Movie:
    """
    Обновляет уровень доступа к фильму
    """
    movie_dal = MovieDAL(session)
    movie = await movie_dal.get_movie(movie_id=movie_id)
        
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")
            
    if not movie.can_modify(user):
        raise HTTPException(status_code=403, detail="You don't have permission to modify this movie")
            
        # Обновляем уровень доступа
    await movie_dal.update_movie(
        movie_id=movie_id,
        access_level=access_level,
        updated_at=datetime.now()
    )
        
        # Получаем обновленный фильм
    updated_movie = await movie_dal.get_movie(movie_id=movie_id)
    return updated_movie 

async def update_all_movies_ratings(session: AsyncSession) -> None:
    """Обновляет рейтинги всех активных фильмов"""
    movie_dal = MovieDAL(session)
    movies = await movie_dal.get_movies()
    
    for movie in movies:
        await movie_dal.update_movie_rating(movie.movie_id) 