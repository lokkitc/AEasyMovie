import os
import sys

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from api.router import main_router
from api.routers import auth, users, movies, comments, episodes, premium
from api.middleware.timing import TimingMiddleware
from config.logging_config import setup_logging
from api.services.premium_service import start_premium_checker
from db.session import async_session
import asyncio
from tasks.background_tasks import start_background_tasks
from core.oauth import setup_oauth
from contextlib import asynccontextmanager

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запускает фоновые задачи при старте приложения и очищает ресурсы при остановке"""
    session = async_session()
    asyncio.create_task(start_premium_checker(session))
    await start_background_tasks()
    yield

app = FastAPI(
    title="API для работы с базой данных",
    description="API для работы с базой данных",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники для теста
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.add_middleware(TimingMiddleware)

setup_oauth(app)

os.makedirs("server/media", exist_ok=True)

app.mount("/media", StaticFiles(directory="server/media", html=True), name="media")

app.include_router(main_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Слушать на всех интерфейсах
        port=port,
        reload=True
    )
    print(f"\nServer is running on http://0.0.0.0:{port}\n")
    print("Press Ctrl+C to stop the server\n")
