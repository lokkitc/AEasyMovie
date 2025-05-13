from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import secrets

import core.config as settings
from schemas.users import Token, UserCreate
from db.models.users import User
from db.session import get_db
from core.security import create_access_token
from api.dependencies.auth import authenticate_user, get_current_user_from_token
from core.oauth import oauth
from api.services.user_service import get_user_by_email, create_new_user
from core.hashing import Hasher

# Настройка логирования
logger = logging.getLogger(__name__)

auth_router = APIRouter()

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db)
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get('/google/login')
async def google_login(request: Request):
    """Начало процесса аутентификации через Google"""
    try:
        # Генерируем случайное состояние
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        
        redirect_uri = request.url_for('google_callback')
        logger.info(f"Starting Google OAuth login with redirect URI: {redirect_uri}")
        
        return await oauth.google.authorize_redirect(
            request,
            redirect_uri,
            state=state,
            access_type='offline',
            prompt='consent'
        )
    except Exception as e:
        logger.error(f"Error in google_login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при инициализации Google OAuth: {str(e)}"
        )

@auth_router.get('/google/callback')
async def google_callback(request: Request, session: AsyncSession = Depends(get_db)):
    """Обработка ответа от Google OAuth"""
    try:
        logger.info("Received Google OAuth callback")
        
        # Проверяем состояние
        state = request.session.get('oauth_state')
        if not state:
            logger.error("No state found in session")
            raise HTTPException(
                status_code=400,
                detail="Отсутствует состояние сессии"
            )
        
        # Получаем токен
        token = await oauth.google.authorize_access_token(request)
        logger.info("Successfully obtained access token")
        
        # Получаем информацию о пользователе
        user_info = token.get('userinfo')
        if not user_info:
            # Если userinfo нет в токене, пробуем получить через API
            user_info = await oauth.google.userinfo()
        
        logger.info(f"Received user info: {user_info}")
        
        if not user_info:
            logger.error("No user info received from Google")
            raise HTTPException(
                status_code=400,
                detail="Не удалось получить информацию о пользователе"
            )
        
        # Проверяем наличие email
        if 'email' not in user_info:
            logger.error("No email in user info")
            raise HTTPException(
                status_code=400,
                detail="Email не найден в данных пользователя"
            )
        
        # Проверяем, существует ли пользователь
        user = await get_user_by_email(user_info['email'], session)
        logger.info(f"Existing user found: {user is not None}")
        
        if not user:
            # Создаем нового пользователя
            logger.info("Creating new user from Google data")
            new_user = UserCreate(
                email=user_info['email'],
                username=user_info['email'].split('@')[0],
                name=user_info.get('given_name', ''),
                surname=user_info.get('family_name', ''),
                password=secrets.token_urlsafe(16)  # Генерируем случайный пароль
            )
            user = await create_new_user(new_user, session)
            logger.info(f"New user created with ID: {user.user_id}")
        
        # Создаем JWT токен
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
            expires_delta=access_token_expires,
        )
        logger.info("JWT token created successfully")
        
        # Очищаем состояние из сессии
        request.session.pop('oauth_state', None)
        
        # Перенаправляем на фронтенд с токеном
        redirect_url = f'http://localhost:5173/auth/callback?token={access_token}'
        logger.info(f"Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url, status_code=303)
        
    except Exception as e:
        logger.error(f"Error in google_callback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка аутентификации через Google: {str(e)}"
        )
