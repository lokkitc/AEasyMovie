from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
import os
from core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY

# Загружаем переменные окружения
config = Config('.env')

# Создаем экземпляр OAuth
oauth = OAuth()

# Конфигурация Google OAuth
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid email profile',
        'redirect_uri': 'http://127.0.0.1:8000/api/auth/google/callback'
    }
)

def setup_oauth(app: FastAPI):
    """Настройка OAuth для приложения"""
    app.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        session_cookie="session",
        max_age=3600,  # 1 час
        same_site="lax",
        https_only=False
    ) 