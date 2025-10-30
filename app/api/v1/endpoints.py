import time
import asyncpg
import logging
from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.schemas import QueryRequest, QueryResponse, DefinitionsResponse
from app.services.query_engine import QueryBuilder
from app.services.semantic_layer import METRICS, DIMENSIONS
from app.core.database import get_db_connection

router = APIRouter(prefix="/v1", tags=["Query Engine"])


@router.get("/definitions", response_model=DefinitionsResponse, tags=["Definitions"])
async def get_definitions():
    return {"metrics": METRICS, "dimensions": DIMENSIONS}


@router.post("/query", response_model=QueryResponse)
async def run_query(
    request: QueryRequest, conn: asyncpg.Connection = Depends(get_db_connection)
):
    start_time = time.perf_counter()

    try:
        builder = QueryBuilder(request)
        sql, params = builder.build()

        logging.debug(f"SQL Gerado: {sql}")
        logging.debug(f"Parâmetros: {params}")

        results = await conn.fetch(sql, *params)

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        data = [dict(record) for record in results]

        return QueryResponse(
            query_sql=sql,
            data=data,
            execution_time_ms=duration_ms,
        )

    except ValueError as e:
        logging.warning(f"Erro de validação na query: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except asyncpg.PostgresError as e:
        logging.error(f"Erro no PostgreSQL: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")

    except Exception as e:
        logging.error(f"Erro inesperado no servidor: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")
