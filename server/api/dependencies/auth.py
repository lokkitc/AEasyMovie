from datetime import timedelta, datetime
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from ...core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    MAX_LOGIN_ATTEMPTS,
    LOGIN_ATTEMPT_WINDOW
)
from schemas.users import Token
from db.dals.user_dal import UserDAL
from db.models.users import User, LoginAttempt
from db.session import get_db
from core.hashing import Hasher
from core.security import create_access_token

login_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
    auto_error=True
)

async def get_user_by_email_for_auth(email: str, session):
    user_dal = UserDAL(session)
    return await user_dal.get_user_by_email(email=email)

async def check_login_attempts(email: str, session: AsyncSession) -> bool:
    """Проверяет количество попыток входа"""
    # Удаляем старые попытки
    await session.execute(
        delete(LoginAttempt).where(
            LoginAttempt.email == email,
            LoginAttempt.created_at < datetime.utcnow() - timedelta(minutes=LOGIN_ATTEMPT_WINDOW)
        )
    )
    
    # Считаем попытки
    result = await session.execute(
        select(LoginAttempt).where(
            LoginAttempt.email == email,
            LoginAttempt.created_at > datetime.utcnow() - timedelta(minutes=LOGIN_ATTEMPT_WINDOW)
        )
    )
    attempts = result.scalars().all()
    
    return len(attempts) < MAX_LOGIN_ATTEMPTS

async def record_login_attempt(email: str, success: bool, session: AsyncSession):
    """Записывает попытку входа"""
    attempt = LoginAttempt(
        email=email,
        success=success,
        created_at=datetime.utcnow()
    )
    session.add(attempt)

async def authenticate_user(email: str, password: str, session) -> Union[User, None]:
    async with session.begin():
        # Проверяем количество попыток
        if not await check_login_attempts(email, session):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )
        
        user = await get_user_by_email_for_auth(email=email, session=session)
        if not user:
            await record_login_attempt(email, False, session)
            return None
            
        if not user.is_active:
            await record_login_attempt(email, False, session)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
            
        if not Hasher.verify_password(password, user.hashed_password):
            await record_login_attempt(email, False, session)
            return None
            
        await record_login_attempt(email, True, session)
        return user

@login_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        
        if not email:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = await get_user_by_email_for_auth(email=email, session=session)
    if not user:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
        
    return user

@login_router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: User = Depends(get_current_user_from_token),
):
    return {"Success": True, "current_user": current_user}