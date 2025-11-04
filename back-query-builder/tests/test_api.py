from fastapi.testclient import TestClient


def test_api_query_sucesso(client: TestClient):
    """
    Testa o endpoint /api/v1/query (caminho feliz).
    Ele usará a conexão mockada do conftest.py
    """
    query_json = {"metrics": ["total_vendas"], "dimensions": ["canal_nome"]}

    response = client.post("/api/v1/query", json=query_json)

    assert response.status_code == 200

    data = response.json()

    expected_data = [
        {
            "metrics": {"total_vendas": 100.0},
            "dimensions": {"canal_nome": "iFood (Mock)"}
        }
    ]

    assert data["data"] == expected_data

    assert "SELECT" in data["query_sql"]
    assert "GROUP BY" in data["query_sql"]

    assert "insights" in data
    
    assert isinstance(data["insights"], list)
    
    assert len(data["insights"]) > 0
    
    assert "iFood (Mock)" in data["insights"][0]


def test_api_query_erro_validacao(client: TestClient):
    """Testa se o endpoint retorna 400 para um request inválido."""
    query_json = {"metrics": ["campo_invalido"], "dimensions": ["canal_nome"]}

    response = client.post("/api/v1/query", json=query_json)

    assert response.status_code == 400
    assert "Campo desconhecido" in response.json()["detail"]