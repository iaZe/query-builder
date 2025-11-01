import time
import asyncpg
import logging
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.v1.schemas import QueryRequest, QueryResponse, DefinitionsResponse
from app.services.ai_translator import AITranslator
from app.core.config import settings
from app.services.query_engine import QueryBuilder
from app.services.semantic_layer import METRICS, DIMENSIONS
from app.core.database import get_db_connection


router = APIRouter(prefix="/v1", tags=["Query Engine"])


@router.get("/definitions", response_model=DefinitionsResponse, tags=["Definitions"])
async def get_definitions():
    """
    Retorna as definições de métricas e dimensões disponíveis
    na camada semântica.
    """

    return {"metrics": METRICS, "dimensions": DIMENSIONS}


async def _execute_query_logic(
    request: QueryRequest,
    conn: asyncpg.Connection,
) -> QueryResponse:
    """
    Lógica compartilhada para executar a query e retornar a resposta.
    """
    start_time = time.perf_counter()

    try:
        builder = QueryBuilder(request)
        sql, params = builder.build()

        chart_suggestion = builder.get_chart_suggestion()

        logging.debug(f"SQL Gerado: {sql}")
        logging.debug(f"Parâmetros: {params}")

        results = await conn.fetch(sql, *params)

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        data = []
        metric_keys = set(request.metrics)
        dimension_keys = set(request.dimensions)

        for record in results:
            record_dict = dict(record)
            metrics_obj = {key: record_dict[key] for key in metric_keys if key in record_dict}
            dimensions_obj = {key: record_dict[key] for key in dimension_keys if key in record_dict}
            
            data.append({"metrics": metrics_obj, "dimensions": dimensions_obj})

        response_obj = QueryResponse(
            query_sql=sql,
            data=data,
            execution_time_ms=duration_ms,
            chart_suggestion=chart_suggestion,
        )

        return response_obj

    except ValueError as e:
        logging.warning(f"Erro de validação na query: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except asyncpg.PostgresError as e:
        logging.error(f"Erro no PostgreSQL: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")

    except Exception as e:
        logging.error(f"Erro inesperado no servidor: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")


@router.post("/query", response_model=QueryResponse)
async def run_query(
    request: QueryRequest,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Endpoint principal que recebe a definição da query (métricas,
    dimensões, filtros) e retorna o resultado.
    """
    return await _execute_query_logic(request, conn)


class TextQueryRequest(BaseModel):
    prompt: str = Field(
        ..., max_length=500, description="A pergunta em linguagem natural."
    )


@router.post("/query-from-text", response_model=QueryResponse, tags=["AI Engine"])
async def run_query_from_text(
    request: TextQueryRequest,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Executa uma query de analytics traduzindo linguagem natural (via IA)
    para o formato JSON do Query Builder.
    """
    translator = AITranslator(api_key=settings.MARITACA_API_KEY)

    try:
        query_json_string = await translator.generate_query_json(request.prompt)

        try:
            query_data = json.loads(query_json_string)
            validated_request = QueryRequest(**query_data)
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"IA gerou um JSON inválido: {e}\nJSON: {query_json_string}")
            raise HTTPException(
                status_code=400,
                detail=f"A IA não conseguiu traduzir o pedido para uma query válida. Tente reformular. (Erro: {e})",
            )

        return await _execute_query_logic(validated_request, conn)

    except Exception as e:
        logging.error(f"Erro no serviço de IA: {e}")
        raise HTTPException(
            status_code=503, detail=f"Erro ao comunicar com o serviço de IA: {e}"
        )
