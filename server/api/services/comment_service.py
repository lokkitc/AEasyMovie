from fastapi import HTTPException
from typing import Union, List
from schemas.comments import CommentCreate, CommentRead
from db.dals.comment_dal import CommentDAL
from db.models.users import User
from db.models.movies import Movie
from sqlalchemy.ext.asyncio import AsyncSession

async def create_new_comment(body: CommentCreate, session: AsyncSession, current_user: User) -> CommentRead:
    comment_dal = CommentDAL(session)
        
    # Проверяем, существует ли фильм
    movie = await session.get(Movie, body.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {body.movie_id} not found")
            
    # Если это ответ на комментарий, проверяем существование родительского комментария
    if body.parent_comment_id:
        parent_comment = await comment_dal.get_comment(body.parent_comment_id)
        if not parent_comment:
            raise HTTPException(status_code=404, detail=f"Parent comment with id {body.parent_comment_id} not found")
        if parent_comment.movie_id != body.movie_id:
            raise HTTPException(status_code=400, detail="Parent comment must be from the same movie")
        
    new_comment = await comment_dal.create_comment(
        content=body.content,
        rating=body.rating,
        movie_id=body.movie_id,
        user_id=current_user.user_id,
        parent_comment_id=body.parent_comment_id
    )
        
    return CommentRead(
        comment_id=new_comment.comment_id,
        user_id=new_comment.user_id,
        movie_id=new_comment.movie_id,
        content=new_comment.content,
        rating=new_comment.rating,
        parent_comment_id=new_comment.parent_comment_id,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at,
        is_active=new_comment.is_active,
        user=current_user
    )

async def delete_comment(comment_id: int, current_user: User, session: AsyncSession) -> Union[int, None]:
    comment_dal = CommentDAL(session)
    comment = await comment_dal.get_comment(comment_id)
        
    if not comment:
        raise HTTPException(status_code=404, detail=f"Comment with id {comment_id} not found")
            
    # Проверяем права на удаление
    if comment.user_id != current_user.user_id and not current_user.can_moderate():
        raise HTTPException(status_code=403, detail="You don't have permission to delete this comment")
            
    deleted_comment_id = await comment_dal.delete_comment(comment_id)
    return deleted_comment_id

async def get_comment(comment_id: int, session: AsyncSession) -> CommentRead:
    comment_dal = CommentDAL(session)
    comment = await comment_dal.get_comment(comment_id)
        
    if not comment:
        raise HTTPException(status_code=404, detail=f"Comment with id {comment_id} not found")
            
    return CommentRead(
        comment_id=comment.comment_id,
        user_id=comment.user_id,
        movie_id=comment.movie_id,
        content=comment.content,
        rating=comment.rating,
        parent_comment_id=comment.parent_comment_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_active=comment.is_active,
        user=comment.user
    )

async def get_movie_comments(movie_id: int, session: AsyncSession) -> List[CommentRead]:
    comment_dal = CommentDAL(session)
    comments = await comment_dal.get_movie_comments(movie_id)
        
    return [CommentRead(
        comment_id=comment.comment_id,
        user_id=comment.user_id,
        movie_id=comment.movie_id,
        content=comment.content,
        rating=comment.rating,
        parent_comment_id=comment.parent_comment_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_active=comment.is_active,
        user=comment.user
    ) for comment in comments]

async def get_comment_replies(comment_id: int, session: AsyncSession) -> List[CommentRead]:
    comment_dal = CommentDAL(session)
    replies = await comment_dal.get_replies(comment_id)
        
    return [CommentRead(
        comment_id=reply.comment_id,
        user_id=reply.user_id,
        movie_id=reply.movie_id,
        content=reply.content,
        rating=reply.rating,
        parent_comment_id=reply.parent_comment_id,
        created_at=reply.created_at,
        updated_at=reply.updated_at,
        is_active=reply.is_active,
        user=reply.user
    ) for reply in replies]

async def update_comment(comment_id: int, updated_comment_params: dict, current_user: User, session: AsyncSession) -> CommentRead:
    comment_dal = CommentDAL(session)
    comment = await comment_dal.get_comment(comment_id)
        
    if not comment:
        raise HTTPException(status_code=404, detail=f"Comment with id {comment_id} not found")
            
    # Проверяем права на обновление
    if comment.user_id != current_user.user_id and not current_user.can_moderate():
        raise HTTPException(status_code=403, detail="You don't have permission to update this comment")
            
    await comment_dal.update_comment(
        comment_id=comment_id,
        **updated_comment_params
    )
        
    updated_comment = await comment_dal.get_comment(comment_id)
        
    return CommentRead(
        comment_id=updated_comment.comment_id,
        user_id=updated_comment.user_id,
        movie_id=updated_comment.movie_id,
        content=updated_comment.content,
        rating=updated_comment.rating,
        parent_comment_id=updated_comment.parent_comment_id,
        created_at=updated_comment.created_at,
        updated_at=updated_comment.updated_at,
        is_active=updated_comment.is_active,
        user=updated_comment.user
    )

async def get_user_comments(user_id: int, session: AsyncSession) -> List[CommentRead]:
    comment_dal = CommentDAL(session)
    comments = await comment_dal.get_user_comments(user_id)
        
    return [CommentRead(
        comment_id=comment.comment_id,
        user_id=comment.user_id,
        movie_id=comment.movie_id,
        content=comment.content,
        rating=comment.rating,
        parent_comment_id=comment.parent_comment_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_active=comment.is_active,
        user=comment.user
    ) for comment in comments] 