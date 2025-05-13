from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.episodes import Episode

class EpisodeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_episode(
        self,
        movie_id: int,
        title: str,
        video_file: str,
        episode_number: int
    ) -> Episode:
        new_episode = Episode(
            movie_id=movie_id,
            title=title,
            video_file=video_file,
            episode_number=episode_number
        )
        self.db_session.add(new_episode)
        await self.db_session.flush()
        await self.db_session.commit()
        return new_episode

    async def get_episode(self, episode_id: int) -> Optional[Episode]:
        query = select(Episode).where(Episode.episode_id == episode_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_episodes_by_movie(self, movie_id: int) -> List[Episode]:
        query = select(Episode).where(Episode.movie_id == movie_id).order_by(Episode.episode_number)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def update_episode(self, episode_id: int, **kwargs) -> Optional[Episode]:
        query = (
            update(Episode)
            .where(Episode.episode_id == episode_id)
            .values(**kwargs)
            .returning(Episode)
        )
        result = await self.db_session.execute(query)
        episode = result.scalar_one_or_none()
        if episode is not None:
            await self.db_session.commit()
        return episode

    async def delete_episode(self, episode_id: int) -> Optional[int]:
        query = delete(Episode).where(Episode.episode_id == episode_id).returning(Episode.episode_id)
        result = await self.db_session.execute(query)
        episode_id = result.scalar_one_or_none()
        if episode_id is not None:
            await self.db_session.commit()
        return episode_id 