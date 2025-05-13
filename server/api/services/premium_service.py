from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from db.dals.user_dal import UserDAL
from db.models.users import User
from fastapi import HTTPException
import asyncio
import logging

logger = logging.getLogger(__name__)

async def check_premium_status(user: User) -> bool:
    """Проверяет и обновляет статус премиум-подписки пользователя"""
    return user.check_and_update_premium_status()

async def check_all_users_premium_status(session: AsyncSession) -> None:
    """Проверяет статус премиум-подписки всех пользователей"""
    try:
        user_dal = UserDAL(session)
        users = await user_dal.get_users()
        
        for user in users:
            if user.is_premium:
                old_status = user.is_premium
                new_status = user.check_and_update_premium_status()
                
                if old_status != new_status:
                    logger.info(f"Premium status changed for user {user.user_id}: {old_status} -> {new_status}")
        
        await session.commit()
    except Exception as e:
        logger.error(f"Error checking premium status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking premium status")

async def start_premium_checker(session: AsyncSession, check_interval: int = 3600) -> None:
    """
    Запускает фоновую задачу для проверки премиум-статуса
    check_interval: интервал проверки в секундах (по умолчанию 1 час)
    """
    while True:
        try:
            await check_all_users_premium_status(session)
            await asyncio.sleep(check_interval)
        except Exception as e:
            logger.error(f"Error in premium checker: {str(e)}")
            await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой 