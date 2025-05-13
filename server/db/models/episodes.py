from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Float
from .base import Base
from db.models.movies import Movie
from db.models.users import User

class Episode(Base):
    __tablename__ = "episodes"

    episode_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.movie_id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    video_file: Mapped[str] = mapped_column(String, nullable=False)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False, default=15.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Отношения
    movie: Mapped[Movie] = relationship("Movie", back_populates="episodes")
    purchased_by: Mapped[list["PurchasedEpisode"]] = relationship("PurchasedEpisode", back_populates="episode")

class PurchasedEpisode(Base):
    __tablename__ = "purchased_episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey("episodes.episode_id"), nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    cost: Mapped[float] = mapped_column(Float, nullable=False)

    # Отношения
    user: Mapped[User] = relationship("User", back_populates="purchased_episodes")
    episode: Mapped[Episode] = relationship("Episode", back_populates="purchased_by") 