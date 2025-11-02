import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db_connection


async def override_get_db_connection():
    """
    Um mock da nossa dependência de banco de dados.
    Isso nos permite testar a API sem um banco real.
    """
    print("Conexão com o banco MOCKADA")
    yield MockAsyncConnection()


class MockAsyncConnection:
    """Simula o objeto de conexão do asyncpg"""

    async def fetch(self, sql: str, *params):
        print(f"MOCK FETCH: {sql} com {params}")
        return [{"total_vendas": 100.0, "canal_nome": "iFood (Mock)"}]


app.dependency_overrides[get_db_connection] = override_get_db_connection


@pytest.fixture
def client():
    """
    Fornece um cliente HTTP para fazer chamadas à nossa API.
    """
    with TestClient(app) as test_client:
        yield test_client
