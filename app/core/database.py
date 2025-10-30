import asyncpg
from typing import AsyncGenerator
from fastapi import HTTPException
from app.core.config import settings

db_pool: asyncpg.Pool = None


async def connect_to_db():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=5,
            max_size=20,
        )
    except Exception as e:
        raise e


async def close_db_connection():
    global db_pool
    if db_pool:
        await db_pool.close()


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    if not db_pool:
        raise HTTPException(
            status_code=500, detail="O pool de conexões não foi inicializado."
        )

    async with db_pool.acquire() as connection:
        yield connection
