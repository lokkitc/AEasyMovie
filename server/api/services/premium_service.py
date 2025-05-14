from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from db.dals.user_dal import UserDAL
from db.models.users import User
from fastapi import HTTPException
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)

# Цены за месяц в разных валютах
PREMIUM_PRICES = {
    "RUB": 299,
    "USD": 4.99,
    "EUR": 4.49
}

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

async def purchase_premium(
    user: User,
    months: int,
    payment_method: str,
    session: AsyncSession
) -> dict:
    """
    Покупка премиум-подписки
    """
    try:
        # Генерируем уникальный ID транзакции
        transaction_id = str(uuid.uuid4())
        
        # Рассчитываем стоимость
        price_rub = PREMIUM_PRICES["RUB"] * months
        
        # Проверяем баланс пользователя
        if user.money < price_rub:
            raise HTTPException(
                status_code=400,
                detail=f"Недостаточно средств. Требуется {price_rub} монет"
            )
        
        # Списываем средства
        user.money -= price_rub
        
        # Добавляем премиум-подписку
        if not user.is_premium or not user.premium_until:
            user.premium_until = datetime.now()
        user.premium_until += timedelta(days=30 * months)
        user.is_premium = True
        
        # Сохраняем изменения
        await session.commit()
        await session.refresh(user)
        
        return {
            "success": True,
            "message": f"Премиум-подписка успешно активирована на {months} месяцев",
            "premium_until": user.premium_until,
            "transaction_id": transaction_id
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error purchasing premium: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при покупке премиум-подписки"
        ) 