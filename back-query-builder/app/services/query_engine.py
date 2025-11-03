import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Optional, Set, Any, Tuple, Dict
from app.api.v1.schemas import QueryRequest, FilterOperator, OrderBy, CustomDateRange
from app.services.semantic_layer import METRICS, DIMENSIONS, JOIN_PATHS


def _build_date_filter(
    date_range_key: Optional[str], custom_range: Optional[CustomDateRange]
) -> Tuple[Optional[str], List[Any]]:
    """
    Traduz o seletor de período (preset ou custom) em um filtro SQL para a
    coluna 'sales.created_at'.

    Retorna uma tupla (sql_clause, params).
    """
    today = datetime.date.today()
    start_date = None
    end_date = today

    if custom_range:
        start_date = custom_range.start_date
        end_date = custom_range.end_date

    elif date_range_key:
        if date_range_key == "last_7_days":
            start_date = today - datetime.timedelta(days=6)
        elif date_range_key == "last_30_days":
            start_date = today - datetime.timedelta(days=29)
        elif date_range_key == "last_6_months":
            start_date = today - relativedelta(months=6)
        elif date_range_key == "last_12_months":
            start_date = today - relativedelta(months=12)
        elif date_range_key == "this_year":
            start_date = today.replace(month=1, day=1)
        else:
            return None, []

    else:
        return None, []

    end_date_exclusive = end_date + datetime.timedelta(days=1)

    return "sales.created_at >= %s AND sales.created_at < %s", [
        start_date,
        end_date_exclusive,
    ]


class QueryBuilder:
    """
    Traduz um objeto QueryRequest (da API) em uma string SQL otimizada.

    Esta classe segue o Princípio Aberto/Fechado (SOLID):
    - É FECHADA para modificação (você não precisa mudar este código para
      adicionar novas funcionalidades).
    - É ABERTA para extensão (você pode adicionar novas métricas/dimensões
      no semantic_layer.py e elas serão suportadas aqui).
    """

    def __init__(self, request: QueryRequest):
        self.request = request

        self.select_clause: List[str] = []
        self.join_clause: List[str] = []
        self.where_clause: List[str] = []
        self.group_by_clause: List[str] = []
        self.order_by_clause: List[str] = []
        self.params: List[Any] = []

        self.param_count: int = 0
        self.required_joins: List[str] = []
        self.field_map: Dict[str, str] = {}

    def build(self) -> Tuple[str, List[Any]]:
        """
        Constrói a query SQL completa e retorna a string SQL
        junto com a lista de parâmetros.
        """

        self._collect_fields_and_joins()

        self._build_select_clause()
        self._build_join_clause()
        self._build_where_clause()
        self._build_group_by_clause()
        self._build_order_by_clause()

        sql = self._construct_final_sql()

        return sql, self.params

    def get_chart_suggestion(self) -> str:
        """
        Implementa a heurística para sugerir o melhor tipo de gráfico
        baseado na query solicitada (número e tipo de métricas/dimensões).
        Retorna uma string específica para o front-end consumir.
        """
        num_metrics = len(self.request.metrics)
        num_dimensions = len(self.request.dimensions)

        if num_dimensions == 0:
            return "Scorecard"

        if num_dimensions == 1:
            dim_name = self.request.dimensions[0]
            dim_info = DIMENSIONS.get(dim_name)
            dim_type = dim_info.get("type", "category") if dim_info else "category"

            if num_metrics == 1:
                if dim_type == "time":
                    return "LineChart"
                if dim_type == "geographic":
                    return "MapChart"
                if dim_type == "category":
                    return "PieChart"

            if num_metrics > 1:
                if dim_type == "time":
                    if num_metrics == 2:
                        return "BiaxialLineChart"
                    else:
                        return "MultiLineChart"
                if dim_type == "category":
                    return "GroupedBarChart"

        if num_dimensions >= 2:
            dim_types = set()
            for dim_name in self.request.dimensions:
                dim_info = DIMENSIONS.get(dim_name)
                if dim_info:
                    dim_types.add(dim_info.get("type", "category"))

            if num_metrics == 1 and "time" in dim_types and "category" in dim_types:
                return "MultiLineChart"

        return "Table"

    def _collect_fields_and_joins(self):
        """
        Coleta todos os campos usados na query (métricas, dimensões,
        filtros, ordenações) e resolve os joins necessários.
        """

        all_field_names = set(self.request.metrics) | set(self.request.dimensions)
        all_field_names.update(f.field for f in self.request.filters)
        all_field_names.update(o.field for o in self.request.order_by)

        for field_name in all_field_names:
            field_info = METRICS.get(field_name) or DIMENSIONS.get(field_name)

            if not field_info:
                raise ValueError(
                    f"Campo desconhecido: '{field_name}' não foi encontrado na camada semântica."
                )

            self.field_map[field_name] = field_info["sql"]

            if "joins_needed" in field_info:
                for join_name in field_info["joins_needed"]:
                    self._add_join_with_dependencies(join_name)

    def _add_join_with_dependencies(self, join_name: str):
        """
        Adiciona um join e suas dependências recursivamente.
        """

        if join_name in self.required_joins:
            return

        join_info = JOIN_PATHS.get(join_name)
        if not join_info:
            raise ValueError(
                f"Configuração de Join inválida: '{join_name}' não encontrado em JOIN_PATHS."
            )

        dependencies = join_info.get("depends_on")
        if dependencies:
            for dependency in dependencies:
                self._add_join_with_dependencies(dependency)

        if join_name not in self.required_joins:
            self.required_joins.append(join_name)

    def _build_join_clause(self):
        """
        Constrói a cláusula JOIN baseada nos joins necessários.
        """

        for join_name in self.required_joins:
            join_info = JOIN_PATHS.get(join_name)
            if join_info:
                self.join_clause.append(join_info["sql"])
            else:
                raise ValueError(
                    f"Join '{join_name}' é necessário mas não foi encontrado em JOIN_PATHS."
                )

    def _build_select_clause(self):
        """
        Constrói a cláusula SELECT usando os aliases (AS).
        """

        for metric_name in self.request.metrics:
            sql = self.field_map[metric_name]
            self.select_clause.append(f'{sql} AS "{metric_name}"')

        for dim_name in self.request.dimensions:
            sql = self.field_map[dim_name]
            self.select_clause.append(f'{sql} AS "{dim_name}"')

    def _build_where_clause(self):
        """
        Constrói a cláusula WHERE com base nos filtros.
        """

        sql_date_fragment, date_params = _build_date_filter(
            self.request.dateRange, self.request.customDateRange
        )

        if sql_date_fragment:

            if date_params:
                placeholder1 = self._get_next_placeholder()
                sql_date_fragment = sql_date_fragment.replace("%s", placeholder1, 1)

                if len(date_params) > 1:
                    placeholder2 = self._get_next_placeholder()
                    sql_date_fragment = sql_date_fragment.replace("%s", placeholder2, 1)

            self.where_clause.append(sql_date_fragment)
            self.params.extend(date_params)

        for f in self.request.filters:
            field_sql = self.field_map[f.field]
            sql_fragment, params = self._build_filter_fragment(
                field_sql, f.operator, f.value
            )

            self.where_clause.append(sql_fragment)
            self.params.extend(params)

    def _get_next_placeholder(self) -> str:
        """
        Retorna o próximo placeholder numerando os parâmetro (ex: $1, $2)
        """

        self.param_count += 1
        return f"${self.param_count}"

    def _build_filter_fragment(
        self, field_sql: str, op: FilterOperator, value: Any
    ) -> Tuple[str, List[Any]]:
        """
        Constrói o fragmento SQL para um filtro específico
        baseado no operador e valor.
        """

        op_map = {
            FilterOperator.EQ: "=",
            FilterOperator.NEQ: "!=",
            FilterOperator.GT: ">",
            FilterOperator.GTE: ">=",
            FilterOperator.LT: "<",
            FilterOperator.LTE: "<=",
        }

        if op in op_map:
            placeholder = self._get_next_placeholder()
            return f"{field_sql} {op_map[op]} {placeholder}", [value]

        if op == FilterOperator.CONTAINS:
            placeholder = self._get_next_placeholder()
            return f"{field_sql} LIKE {placeholder}", [f"%{value}%"]

        if op == FilterOperator.IN:
            placeholder = self._get_next_placeholder()
            return f"{field_sql} = ANY({placeholder})", [value]

        if op == FilterOperator.NOT_IN:
            placeholder = self._get_next_placeholder()
            return f"{field_sql} != ALL({placeholder})", [value]

        if op == FilterOperator.BETWEEN:
            placeholder1 = self._get_next_placeholder()
            placeholder2 = self._get_next_placeholder()
            return f"{field_sql} BETWEEN {placeholder1} AND {placeholder2}", [
                value[0],
                value[1],
            ]

        raise ValueError(f"Operador de filtro desconhecido: {op}")

    def _build_group_by_clause(self):
        """
        Constrói a cláusula GROUP BY baseada nas dimensões.
        """

        if not self.request.dimensions:
            return

        for dim_name in self.request.dimensions:
            self.group_by_clause.append(self.field_map[dim_name])

    def _build_order_by_clause(self):
        """
        Constrói a cláusula ORDER BY baseada nas regras de ordenação.
        """

        allowed_fields = set(self.request.metrics) | set(self.request.dimensions)

        for order in self.request.order_by:
            if order.field not in allowed_fields:
                raise ValueError(
                    f"Campo de ordenação inválido: '{order.field}'. "
                    "Só é permitido ordenar por métricas ou dimensões da query."
                )

            direction = order.direction.value.upper()
            self.order_by_clause.append(f'"{order.field}" {direction}')

    def _construct_final_sql(self) -> str:
        """
        Constrói a query SQL final combinando todas as cláusulas.
        """

        if not self.select_clause:
            raise ValueError(
                "A query não pode ser construída sem métricas ou dimensões."
            )

        select_str = f"SELECT {', '.join(self.select_clause)}"
        from_str = "FROM sales"
        join_str = "\n".join(self.join_clause)

        where_str = ""
        if self.where_clause:
            where_str = f"WHERE {' AND '.join(self.where_clause)}"

        group_by_str = ""
        if self.group_by_clause:
            group_by_str = f"GROUP BY {', '.join(self.group_by_clause)}"

        order_by_str = ""
        if self.order_by_clause:
            order_by_str = f"ORDER BY {', '.join(self.order_by_clause)}"

        limit_str = ""
        if self.request.limit:
            limit_str = f"LIMIT {self.request.limit}"

        query_parts = [
            select_str,
            from_str,
            join_str,
            where_str,
            group_by_str,
            order_by_str,
            limit_str,
        ]

        return "\n".join(part for part in query_parts if part)
