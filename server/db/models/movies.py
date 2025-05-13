from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, DateTime, Float, Text, ForeignKey, Enum as SQLAlchemyEnum, ARRAY
from enum import Enum
from .base import Base
from db.models.users import User

DEFAULT_POSTER = "https://i.pinimg.com/736x/fd/02/55/fd02556bc6ce735541793834bd8725ce.jpg"
DEFAULT_BACKDROP = "https://i.pinimg.com/736x/9b/4d/ab/9b4dab17886caaab85a4a7eec70a3792.jpg"



class MovieAccessLevel(str, Enum):
    PUBLIC = "PUBLIC"  # Доступен всем
    REGISTERED = "REGISTERED"  # Только зарегистрированным пользователям
    MODERATED = "MODERATED"  # Требуется модерация
    PRIVATE = "PRIVATE"  # Только для определенных пользователей

class Movie(Base):
    __tablename__ = "movies"

    movie_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    title: Mapped[str] = mapped_column(String, nullable=False)
    original_title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    poster: Mapped[str] = mapped_column(String, nullable=False, default=DEFAULT_POSTER)
    backdrop: Mapped[str] = mapped_column(String, nullable=False, default=DEFAULT_BACKDROP)

    movie_url: Mapped[str] = mapped_column(String, nullable=True)

    release_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # в минутах
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    director: Mapped[str] = mapped_column(String, nullable=False)
    genres: Mapped[str] = mapped_column(String, nullable=False)  # список жанров через запятую

    likes: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=[])
    dislikes: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=[])
    
    access_level: Mapped[MovieAccessLevel] = mapped_column(SQLAlchemyEnum(MovieAccessLevel), nullable=False, default=MovieAccessLevel.PUBLIC)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    owner: Mapped[User] = relationship("User", back_populates="owned_movies")
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Отношения
    comments: Mapped[list['Comment']] = relationship("Comment", back_populates="movie")
    episodes: Mapped[list['Episode']] = relationship("Episode", back_populates="movie")

    def can_access(self, user: 'User') -> bool:
        # Если фильм неактивен, доступ запрещен
        if not self.is_active:
            return False

        # Владелец всегда имеет доступ
        if user.user_id == self.owner_id:
            return True

        # Суперадмин всегда имеет доступ
        if user.is_superadmin():
            return True

        # Админ всегда имеет доступ
        if user.is_admin():
            return True

        # Публичный фильм доступен всем
        if self.access_level == MovieAccessLevel.PUBLIC:
            return True

        # Для зарегистрированных пользователей
        if self.access_level == MovieAccessLevel.REGISTERED:
            return user.is_active

        # Для модерации
        if self.access_level == MovieAccessLevel.MODERATED:
            return user.can_moderate()

        # Приватный фильм доступен только владельцу
        return False

    def can_modify(self, user: 'User') -> bool:
        # Если фильм неактивен, модификация запрещена
        if not self.is_active:
            return False

        # Владелец может модифицировать
        if user.user_id == self.owner_id:
            return True

        # Суперадмин может модифицировать
        if user.is_superadmin():
            return True

        # Админ может модифицировать
        if user.is_admin():
            return True

        # Модератор может модифицировать только публичные фильмы
        if user.can_moderate():
            return self.access_level == MovieAccessLevel.PUBLIC

        return False

    def can_delete(self, user: 'User') -> bool:
        """
        Проверяет, может ли пользователь удалить фильм
        """
        # Владелец может удалить
        if user.user_id == self.owner_id:
            return True

        # Суперадмин может удалить
        if user.is_superadmin():
            return True

        # Админ может удалить
        if user.is_admin():
            return True

        # Модератор может удалить только публичные фильмы
        if user.can_moderate():
            return self.access_level == MovieAccessLevel.PUBLIC

        return False 