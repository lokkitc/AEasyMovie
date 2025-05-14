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
import os
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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
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
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
    print("\nServer is running on http://127.0.0.1:8000\n")
    print("Press Ctrl+C to stop the server\n")
