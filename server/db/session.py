from typing import Generator


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

import core.config as config


engine = create_async_engine(config.REAL_DATABASE_URL, echo=True, future=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> Generator:
    try:
        session = async_session()
        yield session
    finally:
        await session.close()

