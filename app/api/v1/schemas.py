from pydantic import BaseModel, field_validator, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class FilterOperator(str, Enum):
    """Operadores de filtro que suportamos."""

    EQ = "eq"  # Igual
    NEQ = "neq"  # Não-igual
    GT = "gt"  # Maior que
    GTE = "gte"  # Maior ou igual
    LT = "lt"  # Menor que
    LTE = "lte"  # Menor ou igual
    IN = "in"  # Em (para listas)
    NOT_IN = "not_in"  # Não em
    BETWEEN = "between"  # Entre dois valores
    CONTAINS = "contains"  # Para strings (LIKE)


class SortDirection(str, Enum):
    """Direção da ordenação."""

    ASC = "asc"
    DESC = "desc"


class Filter(BaseModel):
    """Define um único filtro a ser aplicado."""

    field: str
    operator: FilterOperator
    value: Any

    @field_validator("operator")
    def validate_value_for_operator(cls, v, values):
        operator = v
        value = values.data.get("value")

        if operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            if not isinstance(value, list):
                raise ValueError(
                    f"Operador '{operator}' requer um 'value' do tipo lista."
                )

        if operator == FilterOperator.BETWEEN:
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError(
                    f"Operador '{operator}' requer um 'value' com dois elementos (ex: [10, 20])."
                )

        return v


class OrderBy(BaseModel):
    """Define uma regra de ordenação."""

    field: str
    direction: SortDirection = SortDirection.ASC


class QueryRequest(BaseModel):
    """O corpo da requisição de query."""

    metrics: List[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="A lista de métricas (agregações) a serem calculadas.",
    )
    dimensions: List[str] = Field(
        [],
        max_length=10,
        description="A lista de dimensões (GROUP BY) para quebrar as métricas.",
    )
    filters: Optional[List[Filter]] = Field(
        [], max_length=30, description="A lista de filtros (WHERE) para a query."
    )
    order_by: Optional[List[OrderBy]] = Field(
        [], max_length=10, description="Regras de ordenação."
    )
    limit: Optional[int] = Field(
        1000,
        le=100_000,  # le = Less than or Equal to
        description="Limite de linhas. Padrão 1000. Máximo 100.000.",
    )
    dateRange: Optional[str] = None

    @field_validator("metrics")
    def metrics_must_not_be_empty(cls, v):
        return v
    
class DataRow(BaseModel):
    """
    Representa uma única linha de resultado, com métricas e dimensões
    separadas para facilitar o consumo do front-end.
    """
    metrics: Dict[str, Any]
    dimensions: Dict[str, Any]


class QueryResponse(BaseModel):
    """Define a resposta que nossa API enviará de volta."""

    query_sql: str
    data: List[DataRow]
    execution_time_ms: float
    chart_suggestion: str


class DefinitionItem(BaseModel):
    """
    Descreve uma única Métrica ou Dimensão disponível.
    """

    sql: str
    label: str
    type: Optional[str] = None
    joins_needed: Optional[List[str]] = []


class DefinitionsResponse(BaseModel):
    """Retorna o "cardápio" de opções de query."""

    metrics: Dict[str, DefinitionItem]
    dimensions: Dict[str, DefinitionItem]
