from sqlalchemy import update, delete, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Union, List, Optional
from db.models.comments import Comment
from db.dals.base_dal import BaseDAL
from datetime import datetime

class CommentDAL(BaseDAL):
    async def create_comment(
        self,
        content: str,
        rating: int,
        movie_id: int,
        user_id: int,
        parent_comment_id: Optional[int] = None
    ) -> Comment:
        new_comment = Comment(
            content=content,
            rating=rating,
            movie_id=movie_id,
            user_id=user_id,
            parent_comment_id=parent_comment_id
        )
        self.db_session.add(new_comment)
        await self.db_session.flush()
        await self.db_session.commit()
        return new_comment
    
    async def delete_comment(self, comment_id: int) -> Union[int, None]:
        query = update(Comment).where(and_(
            Comment.comment_id == comment_id,
            Comment.is_active == True
        )).values(is_active=False).returning(Comment.comment_id)
        result = await self.db_session.execute(query)
        deleted_comment_id = result.fetchone()
        if deleted_comment_id is not None:
            return deleted_comment_id[0]
        return None
    
    async def get_comment(self, comment_id: int) -> Union[Comment, None]:
        query = select(Comment).options(
            selectinload(Comment.user)
        ).where(Comment.comment_id == comment_id)
        result = await self.db_session.execute(query)
        comment = result.fetchone()
        if comment is not None:
            return comment[0]
        return None
    
    async def get_movie_comments(self, movie_id: int) -> List[Comment]:
        query = select(Comment).options(
            selectinload(Comment.user)
        ).where(and_(
            Comment.movie_id == movie_id,
            Comment.is_active == True,
            Comment.parent_comment_id == None  # Получаем только корневые комментарии
        ))
        result = await self.db_session.execute(query)
        comments = result.fetchall()
        return [comment[0] for comment in comments]
    
    async def get_replies(self, parent_comment_id: int) -> List[Comment]:
        query = select(Comment).options(
            selectinload(Comment.user)
        ).where(and_(
            Comment.parent_comment_id == parent_comment_id,
            Comment.is_active == True
        ))
        result = await self.db_session.execute(query)
        replies = result.fetchall()
        return [reply[0] for reply in replies]

    async def update_comment(self, comment_id: int, **kwargs) -> Union[int, None]:
        query = update(Comment).\
            where(and_(Comment.comment_id == comment_id, Comment.is_active == True)).\
            values(**kwargs, updated_at=datetime.now()).\
            returning(Comment.comment_id)
        res = await self.db_session.execute(query)
        update_comment_id_row = res.fetchone()
        if update_comment_id_row is not None:
            return update_comment_id_row[0]
        return None

    async def get_user_comments(self, user_id: int) -> List[Comment]:
        query = select(Comment).options(
            selectinload(Comment.user)
        ).where(
            Comment.user_id == user_id,
            Comment.is_active == True
        ).order_by(Comment.created_at.desc())
        result = await self.db_session.execute(query)
        return result.scalars().all() 