import pytest
from app.api.v1.schemas import QueryRequest
from app.services.query_engine import QueryBuilder


def test_query_builder_simples():
    """
    Testa uma query simples com métrica, dimensão e filtro.
    Valida se o SQL gerado e os parâmetros estão 100% corretos.
    """
    request_json = {
        "metrics": ["total_vendas"],
        "dimensions": ["canal_nome"],
        "filters": [{"field": "canal_nome", "operator": "eq", "value": "iFood"}],
    }
    request = QueryRequest(**request_json)

    builder = QueryBuilder(request)
    sql, params = builder.build()

    expected_sql = """
        SELECT SUM(sales.total_amount) AS "total_vendas", channels.name AS "canal_nome"
        FROM sales
        LEFT JOIN channels ON sales.channel_id = channels.id
        WHERE channels.name = $1
        GROUP BY channels.name
        LIMIT 1000
    """

    assert " ".join(sql.split()) == " ".join(expected_sql.split())

    assert params == ["iFood"]


def test_query_builder_campo_invalido():
    """Testa se o builder levanta um erro com um campo desconhecido."""
    request_json = {"metrics": ["metrica_fantasma"], "dimensions": []}
    request = QueryRequest(**request_json)

    with pytest.raises(ValueError, match="Campo desconhecido"):
        QueryBuilder(request).build()
