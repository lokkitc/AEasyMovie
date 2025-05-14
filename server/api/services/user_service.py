from fastapi import HTTPException
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from schemas.users import (
    UserCreate,
    UserRead,
    UserReadLimited,
    UserUpdateRequest,
    UserRoleUpdateResponse,
    MoneyTransactionRequest,
    MoneyTransactionResponse,
    LevelUpdateResponse
)
from db.dals.user_dal import UserDAL
from db.models.users import User, UserRole
from core.hashing import Hasher

async def create_new_user(body: UserCreate, session) -> UserRead:
    user_dal = UserDAL(session)
    new_user = await user_dal.create_user(
        name=body.name,
        surname=body.surname,
        email=body.email,
        hashed_password=Hasher.get_password_hash(body.password),
        role=UserRole.USER,
        username=body.username,
    )
    return UserRead(
        user_id=new_user.user_id,
        name=new_user.name,
        surname=new_user.surname,
        email=new_user.email,
        is_active=new_user.is_active,
        username=new_user.username,
        photo=new_user.photo,
        header_photo=new_user.header_photo,
        frame_photo=new_user.frame_photo,
        about=new_user.about,
        location=new_user.location,
        age=new_user.age,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        role=new_user.role
    )

async def delete_user(user_id: int, current_user: User, session) -> Union[int, None]:
    user_dal = UserDAL(session)
    target_user = await user_dal.get_user(user_id=user_id)
    
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        
    if not current_user.can_modify_user(target_user):
        raise HTTPException(status_code=403, detail="You don't have permission to delete this user")
        
    # Деактивируем пользователя вместо удаления
    await user_dal.update_user(
        user_id=user_id,
        is_active=False,
        updated_at=datetime.now()
    )
    
    return user_id

async def get_user(user_id, session) -> Union[UserRead, None]:
    user_dal = UserDAL(session)
    user = await user_dal.get_user(user_id=user_id)
    if user is not None:
        return UserRead(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
            username=user.username,
            photo=user.photo,
            header_photo=user.header_photo,
            frame_photo=user.frame_photo,
            about=user.about,
            location=user.location,
            age=user.age,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role=user.role,
            is_premium=user.is_premium,
            premium_until=user.premium_until,
            money=user.money,
            level=user.level,
            title=user.title
        )
    return None

async def get_user_limited(user_id, session) -> Union[UserReadLimited, None]:
    user_dal = UserDAL(session)
    user = await user_dal.get_user(user_id=user_id)
    if user is not None:
        return UserReadLimited(
            user_id=user.user_id,
            username=user.username,
            photo=user.photo,
            header_photo=user.header_photo,
            about=user.about,
            location=user.location,
            age=user.age,
            created_at=user.created_at,
            is_premium=user.is_premium,
            level=user.level,
            title=user.title
        )
    return None

async def get_user_by_username(username, session) -> Union[UserRead, None]:
    user_dal = UserDAL(session)
    user = await user_dal.get_user_by_username(username=username)
    if user is not None:
        return UserRead(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
            username=user.username,
            photo=user.photo,
            header_photo=user.header_photo,
            frame_photo=user.frame_photo,
            about=user.about,
            location=user.location,
            age=user.age,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role=user.role
        )
    raise HTTPException(status_code=404, detail=f"User with username {username} not found")

async def get_users(session) -> list[UserRead]:
    user_dal = UserDAL(session)
    users = await user_dal.get_users()
    return [UserRead(
        user_id=user.user_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
        username=user.username,
        photo=user.photo,
        header_photo=user.header_photo,
        frame_photo=user.frame_photo,
        about=user.about,
        location=user.location,
        age=user.age,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role=user.role,
        is_premium=user.is_premium,
        premium_until=user.premium_until,
        money=user.money,
        level=user.level,
        title=user.title
    ) for user in users]

def check_user_permissions(target_user: User, current_user: User) -> bool:
    return current_user.can_modify_user(target_user)

async def update_user(updated_user_params: dict, user_id: int, current_user: User, session) -> UserRead:
    user_dal = UserDAL(session)
    target_user = await user_dal.get_user(user_id=user_id)
    
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        
    if not current_user.can_modify_user(target_user):
        raise HTTPException(status_code=403, detail="You don't have permission to modify this user")
    
    # Обновляем только те поля, которые были предоставлены
    update_data = {k: v for k, v in updated_user_params.items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=422,
            detail="No valid fields to update"
        )
        
    await user_dal.update_user(
        user_id=user_id,
        **update_data,
        updated_at=datetime.now()
    )
    
    # Получаем обновленного пользователя
    updated_user = await user_dal.get_user(user_id=user_id)
    if not updated_user:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve updated user"
        )
    
    return UserRead(
        user_id=updated_user.user_id,
        name=updated_user.name,
        surname=updated_user.surname,
        email=updated_user.email,
        is_active=updated_user.is_active,
        username=updated_user.username,
        photo=updated_user.photo,
        header_photo=updated_user.header_photo,
        frame_photo=updated_user.frame_photo,
        about=updated_user.about,
        location=updated_user.location,
        age=updated_user.age,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        role=updated_user.role,
        is_premium=updated_user.is_premium,
        premium_until=updated_user.premium_until,
        money=updated_user.money,
        level=updated_user.level,
        title=updated_user.title
    )

async def update_user_role(user_id: int, role: UserRole, current_user: User, session) -> UserRoleUpdateResponse:
    user_dal = UserDAL(session)
    target_user = await user_dal.get_user(user_id=user_id)
    
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        
    if not current_user.is_superadmin():
        raise HTTPException(status_code=403, detail="Only superadmin can modify user roles")
        
    if target_user.is_superadmin() and not current_user.is_superadmin():
        raise HTTPException(status_code=403, detail="Cannot modify superadmin role")
            
    if role == UserRole.USER and target_user.is_superadmin():
        raise HTTPException(status_code=403, detail="Cannot downgrade superadmin to user")
            
    await user_dal.update_user_role(
        user_id=user_id,
        new_role=role
    )
        
    updated_user = await user_dal.get_user(user_id=user_id)
    if not updated_user:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve updated user"
        )
        
    return UserRoleUpdateResponse(
        user_id=updated_user.user_id,
        role=updated_user.role
    )

async def get_user_by_email(email: str, session: AsyncSession) -> User | None:
    user_dal = UserDAL(session)
    return await user_dal.get_user_by_email(email)

async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
    user_dal = UserDAL(session)
    return await user_dal.get_user_by_id(user_id)

async def add_money(
    db: AsyncSession,
    user_id: int,
    amount: float,
    current_user: User
) -> float:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if current_user.user_id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="У вас нет прав для добавления денег этому пользователю"
        )
    
    user.money += amount
    await db.commit()
    await db.refresh(user)
    return user.money

async def update_user_level(user_id: int, new_level: int, session: AsyncSession, current_user: User) -> dict:
    """Обновить уровень пользователя"""
    user_dal = UserDAL(session)
    user = await user_dal.get_user(user_id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if not current_user.can_modify_user(user):
        raise HTTPException(status_code=403, detail="У вас нет прав для изменения уровня этого пользователя")
    # Определяем титул на основе уровня
    title = "Новичок"
    if new_level < 5:
        title = "Новичок"
    elif new_level < 10:
        title = "Активный пользователь"
    elif new_level < 20:
        title = "Опытный пользователь"
    elif new_level < 50:
        title = "Ветеран"
    else:
        title = "Легенда"
    
    user.level = new_level
    user.title = title
    await session.commit()
    await session.refresh(user)
    
    return {
        "message": f"Уровень обновлен до {new_level}",
        "new_level": user.level,
        "new_title": user.title
    }

async def check_premium_status(user: User) -> bool:
    """Проверяет статус премиум-подписки пользователя"""
    return user.is_premium_active()

