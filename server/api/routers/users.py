from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import os
import shutil
from datetime import datetime

from api.dependencies.auth import get_current_user_from_token as get_current_user
from schemas.users import (
    UserCreate,
    UserRead,
    UserReadLimited,
    UserDeleteResponse,
    UserUpdateRequest,
    UserUpdateResponse,
    UserRoleUpdate,
    UserRoleUpdateResponse,
    MoneyTransactionRequest,
    MoneyTransactionResponse,
    LevelUpdateResponse,
    MoneyAddRequest,
    MoneyAddResponse,
    LevelUpdateRequest
)
from schemas.comments import CommentRead
from api.services.user_service import check_user_permissions
from db.session import get_db
from api.services.user_service import (
    create_new_user,
    delete_user,
    get_user,
    get_user_limited,
    get_users,
    update_user,
    get_user_by_username,
    update_user_role,
    update_user_level,
    add_money
)
from api.services.comment_service import get_user_comments
from db.models.users import User
from api.services.user_service import UserDAL

user_router = APIRouter()

@user_router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Получить полную информацию о текущем пользователе"""
    try:
        user = await get_user(current_user.user_id, session)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Пользователь не найден"
            )
        return user
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@user_router.get("/{user_id}/comments", response_model=list[CommentRead])
async def get_user_comments_router(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[CommentRead]:
    try:
        return await get_user_comments(user_id, session)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@user_router.get("/", response_model=list[UserRead])
async def get_users_router(
    session: AsyncSession = Depends(get_db)
) -> list[UserRead]:
    return await get_users(session)

@user_router.get("/{user_id}", response_model=UserReadLimited)
async def get_user_router(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserReadLimited:
    try:
        user = await get_user_limited(user_id, session)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail=f"User with id {user_id} not found"
            )
        return user
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@user_router.post("/", response_model=UserRead)
async def create_user_router(
    body: UserCreate,
    session: AsyncSession = Depends(get_db)
) -> UserRead:
    return await create_new_user(body, session)

@user_router.patch("/{user_id}", response_model=UserRead)
async def update_user_router(
    user_id: int,
    body: UserUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserRead:
    updated_user_params = body.model_dump(exclude_none=True)
    if not updated_user_params:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided"
        )
    return await update_user(
        updated_user_params=updated_user_params,
        user_id=user_id,
        current_user=current_user,
        session=session
    )

@user_router.delete("/{user_id}", response_model=UserDeleteResponse)
async def delete_user_router(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserDeleteResponse:
    deleted_user_id = await delete_user(user_id, current_user, session)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    return UserDeleteResponse(user_id=deleted_user_id)

@user_router.get("/username/{username}", response_model=UserRead)
async def get_user_by_username_router(
    username: str,
    session: AsyncSession = Depends(get_db)
) -> UserRead:
    user = await get_user_by_username(username, session)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with username {username} not found"
        )
    return user

@user_router.patch("/{user_id}/role", response_model=UserRoleUpdateResponse)
async def update_user_role_router(
    user_id: int,
    body: UserRoleUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserRoleUpdateResponse:
    return await update_user_role(user_id, body.role, current_user, session)

@user_router.post("/{user_id}/money/add", response_model=MoneyAddResponse)
async def add_money_to_user(
    user_id: int,
    money_data: MoneyAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.user_id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="У вас нет прав для добавления денег этому пользователю"
        )
    
    result = await add_money(db, user_id, money_data.amount, current_user)
    return {
        "success": True,
        "message": f"Добавлено {money_data.amount} монет",
        "new_balance": result
    }

@user_router.post("/{user_id}/level/update", response_model=LevelUpdateResponse)
async def update_user_level_router(
    user_id: int,
    body: LevelUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LevelUpdateResponse:
    return await update_user_level(
        user_id=user_id,
        new_level=body.new_level,
        session=session,
        current_user=current_user
    )

@user_router.post("/upload/{type}", response_model=UserRead)
async def upload_user_image(
    type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> UserRead:
    """Загрузка изображения пользователя (аватар или заголовок)"""
    if type not in ['photo', 'header_photo']:
        raise HTTPException(status_code=400, detail="Неверный тип изображения")
        
    # Создаем директорию для изображений пользователя, если она не существует
    user_dir = f"server/media/users/{current_user.user_id}"
    os.makedirs(user_dir, exist_ok=True)
    
    # Генерируем уникальное имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{type}_{timestamp}{file_extension}"
    file_path = os.path.join(user_dir, new_filename)
    
    # Сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")
    finally:
        file.file.close()
    
    # Обновляем путь к файлу в базе данных
    relative_path = f"http://127.0.0.1:8000/media/users/{current_user.user_id}/{new_filename}"
    update_data = {type: relative_path}
    
    return await update_user(
        updated_user_params=update_data,
        user_id=current_user.user_id,
        current_user=current_user,
        session=session
    )

