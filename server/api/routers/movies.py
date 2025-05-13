from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user_from_token as get_current_user
from schemas.movies import (
    MovieCreate,
    MovieRead,
    MovieDeleteResponse,
    MovieUpdateRequest,
    MovieUpdateResponse,
    MovieAccessLevelUpdate,
    MovieAccessLevelResponse
)
from schemas.users import UserRead
from db.session import get_db
from api.services.movie_service import (
    create_new_movie,
    delete_movie,
    get_movie,
    get_movies,
    update_movie,
    check_movie_access,
    check_movie_modify,
    check_movie_delete,
    update_movie_access_level
)
from db.models.users import User

movie_router = APIRouter()

@movie_router.get("/", response_model=list[MovieRead])
async def get_movies_router(
    session: AsyncSession = Depends(get_db)
) -> list[MovieRead]:
    return await get_movies(session)

@movie_router.get("/{movie_id}", response_model=MovieRead)
async def get_movie_router(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    try:
        movie = await get_movie(movie_id, session)
        # if not movie.can_access(current_user):
        #     raise HTTPException(
        #         status_code=403,
        #         detail="У вас нет доступа к этому фильму"
        #     )
        return movie
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_movie_router: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@movie_router.post("/", response_model=MovieRead)
async def create_movie_router(
    body: MovieCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieRead:
    return await create_new_movie(body, session, current_user)

@movie_router.patch("/{movie_id}", response_model=MovieRead)
async def update_movie_router(
    movie_id: int,
    body: MovieUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieRead:
    if not await check_movie_modify(movie_id, current_user, session):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to modify this movie"
        )
    return await update_movie(movie_id, body, session)

@movie_router.delete("/{movie_id}", response_model=MovieUpdateResponse)
async def delete_movie_router(
    movie_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieUpdateResponse:
    if not await check_movie_delete(movie_id, current_user, session):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this movie"
        )
    return await delete_movie(movie_id, session)

@movie_router.patch("/{movie_id}/access", response_model=MovieAccessLevelResponse)
async def update_movie_access_router(
    movie_id: int,
    body: MovieAccessLevelUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieAccessLevelResponse:
    updated_movie = await update_movie_access_level(
        movie_id,
        body.access_level,
        current_user,
        session
    )
    return MovieAccessLevelResponse(
        movie_id=updated_movie.movie_id,
        access_level=updated_movie.access_level
    ) 