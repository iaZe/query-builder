from pydantic import BaseModel, field_validator, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class FilterOperator(str, Enum):

    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    CONTAINS = "contains"


class SortDirection(str, Enum):

    ASC = "asc"
    DESC = "desc"


class Filter(BaseModel):

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

    field: str
    direction: SortDirection = SortDirection.ASC


class QueryRequest(BaseModel):

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
        le=100_000,
        description="Limite de linhas. Padrão 1000. Máximo 100.000.",
    )

    @field_validator("metrics")
    def metrics_must_not_be_empty(cls, v):
        return v


class QueryResponse(BaseModel):

    query_sql: str
    data: List[Dict[str, Any]]
    execution_time_ms: float


class DefinitionItem(BaseModel):

    sql: str
    label: str
    type: Optional[str] = None
    joins_needed: Optional[List[str]] = []


class DefinitionsResponse(BaseModel):

    metrics: Dict[str, DefinitionItem]
    dimensions: Dict[str, DefinitionItem]
