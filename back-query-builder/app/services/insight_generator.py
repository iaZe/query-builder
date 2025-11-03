from typing import Any, Optional, Dict, List
from app.api.v1.schemas import QueryRequest, QueryResponse, DataRow
from app.services.semantic_layer import METRICS, DIMENSIONS

def _format_value(value: Any, metric_type: Optional[str] = "number") -> str:
    """
    Formata um valor numérico para BRL ou número padrão, 
    sem depender do locale do sistema.
    """
    try:
        num = float(value)
        
        if metric_type == "currency":
            formatted_str = f"R$ {num:,.2f}"
            
            return formatted_str.replace(",", "X").replace(".", ",").replace("X", ".")
        
        if metric_type == "percentage":
            return f"{num:.1f}%".replace(".", ",")
        
        if metric_type == "number":
            if num == int(num):
                formatted_str = f"{int(num):,d}"
                return formatted_str.replace(",", ".")
            else:
                formatted_str = f"{num:,.2f}"
                return formatted_str.replace(",", "X").replace(".", ",").replace("X", ".")

        formatted_str = f"{num:,.2f}"
        return formatted_str.replace(",", "X").replace(".", ",").replace("X", ".")

    except (ValueError, TypeError, OverflowError):
        return str(value)

class InsightGenerator:
    """
    Gera um insight textual dinâmico baseado na estrutura de uma 
    QueryRequest e sua QueryResponse.
    """

    def __init__(self, request: QueryRequest, response: QueryResponse):
        self.request = request
        self.response = response
        self.data = response.data
        self.num_metrics = len(request.metrics)
        self.num_dims = len(request.dimensions)

    def _get_field_info(self, field_name: str) -> Dict[str, Any]:
        """Busca a definição (label, type) de um campo."""
        if field_name in METRICS:
            return METRICS[field_name]
        if field_name in DIMENSIONS:
            return DIMENSIONS[field_name]
        return {"label": field_name, "type": "unknown"}

    def generate_text(self) -> Optional[str]:
        """Ponto de entrada principal. Roteia para o gerador correto."""
        if not self.data:
            return "Não foram encontrados dados para esta consulta no período selecionado."

        try:
            if self.num_dims == 0:
                return self._generate_kpi_insight()
            
            if self.num_dims == 1:
                return self._generate_leaderboard_insight()

            if self.num_dims > 1:
                return self._generate_crosstab_insight()
        
        except Exception as e:
            print(f"Erro ao gerar insight: {e}")
            return "Os dados foram processados, mas um insight automático não pôde ser gerado."
        
        return None

    def _generate_kpi_insight(self) -> str:
        """
        Gera insight para queries de "Scorecard" (0 Dimensões).
        Ex: { "metrics": ["total_vendas", "total_pedidos"] }
        """
        row = self.data[0]
        insights = []

        for metric_name, value in row.metrics.items():
            info = self._get_field_info(metric_name)
            label = info.get("label", metric_name)
            m_type = info.get("type", "number")
            f_val = _format_value(value, m_type)
            
            insights.append(f"**{label}** de **{f_val}**")
        
        return f"Visão geral com {', '.join(insights[:-1])} e {insights[-1]}."

    def _generate_leaderboard_insight(self) -> str:
        """
        Gera insight para queries de "Leaderboard" (1 Dimensão).
        Ex: { "metrics": ["total_pedidos"], "dimensions": ["metodo_pagamento"] }
        """
        dim_name = self.request.dimensions[0]
        dim_label = self._get_field_info(dim_name).get("label", dim_name)
        
        top_row = self.data[0]
        top_dim_value = top_row.dimensions.get(dim_name, "N/A")

        metric_insights = []
        for m_name, m_value in top_row.metrics.items():
            info = self._get_field_info(m_name)
            label = info.get("label", m_name)
            m_type = info.get("type", "number")
            f_val = _format_value(m_value, m_type)
            
            metric_insights.append(f"**{label}** de **{f_val}**")
        
        metrics_str = " e ".join(metric_insights)

        contribution_str = ""
        
        primary_metric_name = None
        if self.request.order_by and self.request.order_by[0].direction == "desc":
             primary_metric_name = self.request.order_by[0].field
        elif self.request.metrics:
             primary_metric_name = self.request.metrics[0]

        if primary_metric_name and "medio" not in primary_metric_name.lower():
            try:
                total_value = sum(float(row.metrics[primary_metric_name]) for row in self.data)
                top_value = float(top_row.metrics[primary_metric_name])
                
                if total_value > 0:
                    percentage = (top_value / total_value) * 100
                    p_label = self._get_field_info(primary_metric_name).get("label", primary_metric_name)
                    contribution_str = f", responsável por **{percentage:.1f}%** do {p_label} total".replace(".", ",")
            except Exception:
                contribution_str = ""

        return (
            f"O principal **{dim_label}** é **{top_dim_value}**, "
            f"com {metrics_str}{contribution_str}."
        )

    def _generate_crosstab_insight(self) -> str:
        """
        Gera insight para queries de "Tabela Cruzada" (2+ Dimensões).
        """
        top_row = self.data[0]
        
        dim_insights = []
        for d_name, d_value in top_row.dimensions.items():
            d_label = self._get_field_info(d_name).get("label", d_name)
            dim_insights.append(f"{d_label} **{d_value}**")

        met_insights = []
        for m_name, m_value in top_row.metrics.items():
            m_label = self._get_field_info(m_name).get("label", m_name)
            m_type = self._get_field_info(m_name).get("type", "number")
            f_val = _format_value(m_value, m_type)
            met_insights.append(f"{m_label} de **{f_val}**")

        dims_str = " e ".join(dim_insights)
        mets_str = " e ".join(met_insights)

        return f"A combinação líder foi {dims_str}, que gerou {mets_str}."