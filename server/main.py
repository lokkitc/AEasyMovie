from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from api.router import main_router
from api.routers import auth
from api.middleware.timing import TimingMiddleware
from config.logging_config import setup_logging
from api.services.premium_service import start_premium_checker
from db.session import async_session
import asyncio
import os
from tasks.background_tasks import start_background_tasks
from core.oauth import setup_oauth

setup_logging()

app = FastAPI(
    title="API для работы с базой данных",
    description="API для работы с базой данных"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.add_middleware(TimingMiddleware)

# Настройка OAuth
setup_oauth(app)

# Создаем директорию для медиафайлов, если она не существует
os.makedirs("server/media", exist_ok=True)

# Монтируем статические файлы
app.mount("/media", StaticFiles(directory="server/media", html=True), name="media")

# Регистрация роутеров
app.include_router(main_router, prefix="/api")
app.include_router(auth.auth_router, prefix="/api/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    """Запускает фоновые задачи при старте приложения"""
    session = async_session()
    asyncio.create_task(start_premium_checker(session))
    await start_background_tasks()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
    print("\nServer is running on http://127.0.0.1:8000\n")
    print("Press Ctrl+C to stop the server\n")
