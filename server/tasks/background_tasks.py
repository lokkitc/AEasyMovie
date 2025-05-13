import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import async_session
from api.services.movie_service import update_all_movies_ratings

logger = logging.getLogger(__name__)

async def update_ratings_task():
    """Фоновая задача для обновления рейтингов фильмов"""
    while True:
        try:
            async with async_session() as session:
                await update_all_movies_ratings(session)
                logger.info(f"Рейтинги фильмов обновлены в {datetime.now()}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении рейтингов: {str(e)}")
        
        # Ждем 1 минуту перед следующим обновлением
        await asyncio.sleep(60)

async def start_background_tasks():
    """Запускает все фоновые задачи"""
    try:
        # Запускаем задачу обновления рейтингов
        asyncio.create_task(update_ratings_task())
        logger.info("Фоновые задачи запущены")
    except Exception as e:
        logger.error(f"Ошибка при запуске фоновых задач: {str(e)}") 