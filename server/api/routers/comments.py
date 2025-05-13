from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user_from_token as get_current_user
from schemas.comments import (
    CommentCreate,
    CommentRead,
    CommentDeleteResponse,
    CommentUpdate,
    CommentUpdateResponse
)
from db.session import get_db
from api.services.comment_service import (
    create_new_comment,
    delete_comment,
    get_comment,
    get_movie_comments,
    get_comment_replies,
    update_comment
)
from db.models.users import User

comment_router = APIRouter()

@comment_router.get("/movie/{movie_id}", response_model=list[CommentRead])
async def get_movie_comments_router(
    movie_id: int,
    session: AsyncSession = Depends(get_db)
) -> list[CommentRead]:
    return await get_movie_comments(movie_id, session)

@comment_router.get("/{comment_id}", response_model=CommentRead)
async def get_comment_router(
    comment_id: int,
    session: AsyncSession = Depends(get_db)
) -> CommentRead:
    return await get_comment(comment_id, session)

@comment_router.get("/{comment_id}/replies", response_model=list[CommentRead])
async def get_comment_replies_router(
    comment_id: int,
    session: AsyncSession = Depends(get_db)
) -> list[CommentRead]:
    return await get_comment_replies(comment_id, session)

@comment_router.post("/", response_model=CommentRead)
async def create_comment_router(
    body: CommentCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CommentRead:
    return await create_new_comment(body, session, current_user)

@comment_router.patch("/{comment_id}", response_model=CommentRead)
async def update_comment_router(
    comment_id: int,
    body: CommentUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CommentRead:
    updated_comment_params = body.model_dump(exclude_none=True)
    if not updated_comment_params:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for comment update should be provided"
        )
    return await update_comment(comment_id, updated_comment_params, current_user, session)

@comment_router.delete("/{comment_id}", response_model=CommentDeleteResponse)
async def delete_comment_router(
    comment_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CommentDeleteResponse:
    deleted_comment_id = await delete_comment(comment_id, current_user, session)
    if deleted_comment_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Comment with id {comment_id} not found"
        )
    return CommentDeleteResponse(comment_id=deleted_comment_id) 