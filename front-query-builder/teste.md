Sim, com certeza. Essa é uma excelente ideia e é o "próximo nível" de integração entre o back-end e o front-end.

Em vez de enviar uma string genérica como `"line"`, podemos enviar uma sugestão muito mais específica que o front-end (com Recharts) pode consumir diretamente em um `switch` statement, sem precisar de um "dicionário" de tradução.

A sua sugestão de enviar `"BiaxialLineChart"` para o caso de 2 métricas é perfeita. Ela lida com o caso de uso mais comum para gráficos de eixo duplo (ex: "Receita" em R$ no eixo Y1 e "Pedidos" em unidades no eixo Y2).

Vamos modificar o método `get_chart_suggestion` para retornar essas sugestões mais ricas.

### 📖 Explicação das Mudanças

1.  **Nomes Específicos:** Mudei todos os retornos de genéricos (`"bar"`, `"line"`) para nomes de "tipo" de gráfico (`"BarChart"`, `"LineChart"`).
2.  **Lógica Biaxial (Sua Sugestão):** Adicionei a lógica para verificar `if num_metrics == 2` e retornar `"BiaxialLineChart"`. Para 3 ou mais métricas, ele retorna `"MultiLineChart"`.
3.  **Gráfico de Pizza (PieChart):** Para o caso de `1 Métrica + 1 Categoria`, alterei a sugestão de `"bar"` para `"PieChart"`. Um gráfico de pizza é ideal para essa composição. O front-end pode, então, ter uma regra simples: "Se o `chart_suggestion` for `PieChart`, mas o número de itens (`data.length`) for maior que 7, renderize um `BarChart`".

Aqui está o código atualizado para `app/services/query_engine.py`:

````python
    def get_chart_suggestion(self) -> str:
        """
        Implementa a heurística para sugerir o melhor tipo de gráfico
        baseado na query solicitada (número e tipo de métricas/dimensões).
        Retorna uma string específica para o front-end consumir.
        """
        num_metrics = len(self.request.metrics)
        num_dimensions = len(self.request.dimensions)

        # 1 Métrica, 0 Dimensões (ex: "Faturamento Total")
        if num_dimensions == 0:
            return "Scorecard"

        # 1 Dimensão
        if num_dimensions == 1:
            dim_name = self.request.dimensions[0]
            dim_info = DIMENSIONS.get(dim_name)
            dim_type = dim_info.get("type", "category") if dim_info else "category"

            # 1 Métrica, 1 Dimensão
            if num_metrics == 1:
                if dim_type == "time":
                    return "LineChart"
                if dim_type == "geographic":
                    return "MapChart"
                if dim_type == "category":
                    # Sugere Pizza, front-end pode reverter para BarChart se houver muitos itens
                    return "PieChart"

            # 2+ Métricas, 1 Dimensão
            if num_metrics > 1:
                if dim_type == "time":
                    if num_metrics == 2:
                        # Caso especial para 2 métricas vs tempo (Eixo Duplo)
                        return "BiaxialLineChart"
                    else:
                        # 3+ métricas vs tempo
                        return "MultiLineChart"
                if dim_type == "category":
                    return "GroupedBarChart"

        # 2+ Dimensões
        if num_dimensions >= 2:
            dim_types = set()
            for dim_name in self.request.dimensions:
                dim_info = DIMENSIONS.get(dim_name)
                if dim_info:
                    dim_types.add(dim_info.get("type", "category"))

            # Caso especial: 1 Métrica, 1 Tempo, 1 Categoria (ex: Vendas por Produto ao longo do Tempo)
            if num_metrics == 1 and "time" in dim_types and "category" in dim_types:
                return "MultiLineChart"

        # Fallback: Para todas as outras combinações complexas (ex: 2 métricas + 2 dimensões)
        return "Table"
```Esta é uma excelente ideia e uma refatoração muito inteligente.

Você está correto. Para o front-end, especialmente para bibliotecas de gráfico como o Recharts, é muito mais fácil iterar se ele souber quais chaves são métricas (para os `<Bar dataKey="..." />`) e quais são dimensões (para o `<XAxis dataKey="..." />`).

O formato atual, "plano", força o front-end a ter que "adivinhar" ou filtrar as chaves, o que é uma lógica ruim. O formato que você propôs é muito superior.

Vamos implementar isso. Precisamos alterar 2 arquivos:

1.  **`app/api/v1/schemas.py`**: Para ensinar ao Pydantic a nova estrutura da resposta.
2.  **`app/api/v1/endpoints.py`**: Para formatar os dados da nova maneira *antes* de enviá-los.

-----

### 1\. Atualizar `app/api/v1/schemas.py`

Primeiro, vamos definir o novo "shape" da nossa resposta. Vamos criar um novo modelo `DataRow` e usá-lo na `QueryResponse`.

```python
# app/api/v1/schemas.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

# ... (seus outros schemas como Filter, QueryRequest, etc. continuam aqui) ...

# --- 1. Definir o novo formato de linha de dados ---
class DataRow(BaseModel):
    """
    Representa uma única linha de resultado, com métricas e dimensões
    separadas para facilitar o consumo do front-end.
    """
    metrics: Dict[str, Any]
    dimensions: Dict[str, Any]

# --- 2. Atualizar o QueryResponse ---
class QueryResponse(BaseModel):
    """Define a resposta que nossa API enviará de volta."""
    query_sql: str

    # ANTES:
    # data: List[Dict[str, Any]]

    # DEPOIS:
    data: List[DataRow] # <-- Atualizado para usar nosso novo modelo

    execution_time_ms: float
    chart_suggestion: str

# ... (o resto dos seus schemas) ...
````

---

### 2\. Atualizar `app/api/v1/endpoints.py` (A Lógica Principal)

Agora, vamos atualizar o `_execute_query_logic` para construir essa nova estrutura. A chave aqui é que a função tem acesso ao `request: QueryRequest`, então ela sabe exatamente quais chaves são `metrics` e quais são `dimensions`.

_Nota: Estou usando a versão completa da função, incluindo o cache Redis, pois ela precisa ser atualizada também._

```python
# app/api/v1/endpoints.py
...
# (todos os seus imports)
...

async def _execute_query_logic(
    request: QueryRequest,
    conn: asyncpg.Connection,
    redis_conn: redis.Redis
) -> QueryResponse:
    """
    Função auxiliar que contém a lógica principal:
    1. Checa o cache
    2. Se (MISS): Roda o QueryBuilder, executa no DB, obtém sugestão de gráfico
    3. Formata os dados no novo formato (metrics/dimensions)
    4. Salva no cache
    5. Retorna a resposta
    """
    start_time = time.perf_counter()

    # 1. Lógica de Cache (Início)
    request_json_str = request.model_dump_json(exclude_unset=True) # Usar exclude_unset
    cache_key = f"query:{hashlib.md5(request_json_str.encode('utf-8')).hexdigest()}"

    try:
        cached_result_json = await redis_conn.get(cache_key)
        if cached_result_json:
            logging.info(f"Cache HIT para a chave: {cache_key}")
            cached_result = json.loads(cached_result_json)
            cached_result["execution_time_ms"] = (time.perf_counter() - start_time) * 1000
            return QueryResponse(**cached_result)
    except Exception as e:
        logging.error(f"Erro ao acessar o cache Redis: {e}")

    # --- CACHE MISS ---
    logging.info(f"Cache MISS para a chave: {cache_key}. Executando no DB.")

    try:
        # 1. Construir a Query
        builder = QueryBuilder(request)
        sql, params = builder.build()

        # 2. Obter a Sugestão de Gráfico
        chart_suggestion = builder.get_chart_suggestion()

        logging.debug(f"SQL Gerado: {sql}")
        logging.debug(f"Parâmetros: {params}")

        # 3. Executar a Query
        query_start_time = time.perf_counter()
        results = await conn.fetch(sql, *params)
        db_duration_ms = (time.perf_counter() - query_start_time) * 1000

        # --- 4. FORMATAR A RESPOSTA (A NOVA LÓGICA) ---

        # ANTES:
        # data = [dict(record) for record in results]

        # DEPOIS (Separando métricas e dimensões):
        data = []
        metric_keys = set(request.metrics)
        dimension_keys = set(request.dimensions)

        for record in results:
            record_dict = dict(record)
            metrics_obj = {key: record_dict[key] for key in metric_keys if key in record_dict}
            dimensions_obj = {key: record_dict[key] for key in dimension_keys if key in record_dict}

            data.append({"metrics": metrics_obj, "dimensions": dimensions_obj})

        # --- Fim da Nova Lógica ---

        response_obj = QueryResponse(
            query_sql=sql,
            data=data, # 'data' agora tem o novo formato
            execution_time_ms=db_duration_ms,
            chart_suggestion=chart_suggestion
        )

        # 5. Salvar no Cache
        try:
            # Pydantic v2 usa model_dump_json
            response_json_str = response_obj.model_dump_json()
            await redis_conn.set(cache_key, response_json_str, ex=CACHE_TTL_SECONDS)
        except Exception as e:
            logging.error(f"Erro ao salvar no cache Redis: {e}")

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

# ... (o resto do seu endpoints.py) ...
```

### ⚠️ Próximo Passo (Importante para o Front-end)

Você precisará atualizar seus tipos no TypeScript para espelhar essa mudança.

**Em `src/types/analytics.types.ts`:**

```typescript
// src/types/analytics.types.ts

// ...

// --- 1. Crie o novo tipo DataRow ---
export interface DataRow {
  metrics: Record<string, any>;
  dimensions: Record<string, any>;
}

// --- 2. Atualize o QueryResponse ---
export interface QueryResponse {
  query_sql: string;
  // ANTES:
  // data: Record<string, any>[];
  // DEPOIS:
  data: DataRow[]; // <-- Atualizado
  execution_time_ms: number;
  chart_suggestion: string;
}

// ...
```

Isso garante que seu back-end e front-end permaneçam perfeitamente sincronizados.
