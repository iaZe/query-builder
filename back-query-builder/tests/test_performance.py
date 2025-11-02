import pytest
import httpx
import asyncio

API_URL = "http://localhost:8000/api/v1/query"

PERFORMANCE_TARGET_MS = 500.0

pytestmark = pytest.mark.performance


@pytest.mark.asyncio
async def test_complex_query_performance():
    """
    Testa o tempo de resposta de uma query complexa (mundo real)
    batendo na API e no banco de dados REAIS.
    """

    complex_query_json = {
        "metrics": ["total_produtos_vendidos"],
        "dimensions": ["produto_nome"],
        "filters": [
            {"field": "canal_nome", "operator": "eq", "value": "iFood"},
            {"field": "dia_da_semana", "operator": "eq", "value": 4},
            {"field": "hora_venda", "operator": "gte", "value": 18},
        ],
        "order_by": [{"field": "total_produtos_vendidos", "direction": "desc"}],
        "limit": 10,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, json=complex_query_json, timeout=10.0)

            response.raise_for_status()

            data = response.json()

            assert "data" in data
            assert "execution_time_ms" in data
            assert "query_sql" in data
            assert len(data["data"]) <= 10

            execution_time = data["execution_time_ms"]

            print(f"\n--- Tempo de Execução da Query: {execution_time:.2f} ms ---")

            assert execution_time < PERFORMANCE_TARGET_MS, (
                f"Performance Regrediu! "
                f"Tempo: {execution_time:.2f} ms, "
                f"Alvo: < {PERFORMANCE_TARGET_MS} ms"
            )

        except httpx.ConnectError as e:
            pytest.fail(
                f"Falha ao conectar na API em {API_URL}. "
                f"Você lembrou de iniciar o servidor (uvicorn)? Erro: {e}"
            )
        except httpx.HTTPStatusError as e:
            pytest.fail(
                f"A API retornou um erro {e.response.status_code}. "
                f"Detalhe: {e.response.text}"
            )
