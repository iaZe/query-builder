import asyncpg
import logging
from typing import AsyncGenerator
from fastapi import HTTPException
from app.core.config import settings

db_pool: asyncpg.Pool = None


async def connect_to_db():
    """Cria o pool de conexões."""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=5,
            max_size=20,
        )
        logging.info("Pool de conexões com o PostgreSQL criado com sucesso.")
    except Exception as e:
        logging.critical(f"Falha ao criar o pool de conexões: {e}")
        raise e


async def close_db_connection():
    """Fecha o pool de conexões."""
    global db_pool
    if db_pool:
        await db_pool.close()
        logging.info("Pool de conexões com o PostgreSQL fechado.")


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Fornece uma conexão do pool para uso em requisições."""
    if not db_pool:
        raise HTTPException(
            status_code=500, detail="O pool de conexões não foi inicializado."
        )

    async with db_pool.acquire() as connection:
        yield connection
