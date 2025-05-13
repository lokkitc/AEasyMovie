from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Text
from .base import Base
from db.models.users import User
from db.models.movies import Movie

class Comment(Base):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Связь с пользователем
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    user: Mapped[User] = relationship("User", back_populates="comments")
    
    # Связь с фильмом
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.movie_id"), nullable=False)
    movie: Mapped[Movie] = relationship("Movie", back_populates="comments")
    
    # Основной комментарий
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Рейтинг фильма от пользователя (от 1 до 10)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Родительский комментарий (для обсуждений)
    parent_comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.comment_id"), nullable=True)
    parent: Mapped['Comment'] = relationship("Comment", remote_side=[comment_id], back_populates="replies")
    replies: Mapped[list['Comment']] = relationship("Comment", back_populates="parent")
    
    # Статус комментария
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def validate(self) -> bool:
        if not self.content or len(self.content.strip()) == 0:
            return False
        if self.rating < 1 or self.rating > 10:
            return False
        return True
