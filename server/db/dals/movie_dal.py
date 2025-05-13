from sqlalchemy import update, delete, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, List
from db.models.movies import Movie
from db.dals.base_dal import BaseDAL
from datetime import datetime
from db.models.comments import Comment

class MovieDAL(BaseDAL):
    async def create_movie(
        self,
        title: str,
        original_title: str,
        description: str,
        poster: str,
        backdrop: str,
        release_date: datetime,
        duration: int,
        director: int,
        genres: List[str],
        owner_id: int,
    ) -> Movie:
        new_movie = Movie(
            title=title,
            original_title=original_title,
            description=description,
            poster=poster,
            backdrop=backdrop,
            release_date=release_date,
            duration=duration,
            director=director,
            genres=genres,
            owner_id=owner_id,
        )
        self.db_session.add(new_movie)
        await self.db_session.flush()
        await self.db_session.commit()
        return new_movie
    
    async def delete_movie(self, movie_id: int) -> Union[int, None]:
        query = update(Movie).where(and_(
            Movie.movie_id == movie_id,
            Movie.is_active == True
        )).values(is_active=False).returning(Movie.movie_id)
        result = await self.db_session.execute(query)
        deleted_movie_id = result.fetchone()
        if deleted_movie_id is not None:
            await self.db_session.commit()
            return deleted_movie_id[0]
        return None
    
    async def get_movie(self, movie_id: int) -> Union[Movie, None]:
        query = select(Movie).where(and_(
            Movie.movie_id == movie_id,
            Movie.is_active == True
        ))
        result = await self.db_session.execute(query)
        movie = result.scalar_one_or_none()
        return movie
    
    async def get_movies(self) -> List[Movie]:
        query = select(Movie).where(Movie.is_active == True)
        result = await self.db_session.execute(query)
        movies = result.fetchall()
        return [movie[0] for movie in movies]

    async def update_movie(self, movie_id: int, **kwargs) -> Union[int, None]:
        query = update(Movie).\
            where(and_(Movie.movie_id == movie_id, Movie.is_active == True)).\
            values(kwargs).\
            returning(Movie.movie_id)
        res = await self.db_session.execute(query)
        update_movie_id_row = res.fetchone()
        if update_movie_id_row is not None:
            await self.db_session.commit()
            return update_movie_id_row[0]
        return None 

    async def update_movie_rating(self, movie_id: int) -> Union[float, None]:
        """Обновляет рейтинг фильма на основе среднего значения оценок из комментариев"""
        query = select(Movie).where(and_(
            Movie.movie_id == movie_id,
            Movie.is_active == True
        ))
        result = await self.db_session.execute(query)
        movie = result.scalar_one_or_none()
        
        if movie is not None:
            # Получаем все активные комментарии для фильма
            comments_query = select(Comment).where(and_(
                Comment.movie_id == movie_id,
                Comment.is_active == True
            ))
            comments_result = await self.db_session.execute(comments_query)
            comments = comments_result.scalars().all()
            
            if comments:
                # Вычисляем средний рейтинг
                total_rating = sum(comment.rating for comment in comments)
                average_rating = total_rating / len(comments)
                
                # Обновляем рейтинг фильма
                update_query = update(Movie).\
                    where(Movie.movie_id == movie_id).\
                    values(rating=round(average_rating, 1))
                await self.db_session.execute(update_query)
                await self.db_session.commit()
                
                return round(average_rating, 1)
        return None 