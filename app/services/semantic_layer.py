from enum import Enum


class JoinType(str, Enum):
    INNER = "JOIN"
    LEFT = "LEFT JOIN"


JOIN_PATHS = {
    "stores": {
        "sql": "LEFT JOIN stores ON sales.store_id = stores.id",
        "depends_on": [],
        "type": JoinType.LEFT,
    },
    "channels": {
        "sql": "LEFT JOIN channels ON sales.channel_id = channels.id",
        "depends_on": [],
        "type": JoinType.LEFT,
    },
    "customers": {
        "sql": "LEFT JOIN customers ON sales.customer_id = customers.id",
        "depends_on": [],
        "type": JoinType.LEFT,
    },
    "product_sales": {
        "sql": "JOIN product_sales ON sales.id = product_sales.sale_id",
        "depends_on": [],
        "type": JoinType.INNER,
    },
    "products": {
        "sql": "JOIN products ON product_sales.product_id = products.id",
        "depends_on": ["product_sales"],
        "type": JoinType.INNER,
    },
    "categories": {
        "sql": "JOIN categories ON products.category_id = categories.id",
        "depends_on": ["products"],
        "type": JoinType.LEFT,
    },
    "payment_types": {
        "sql": """
            JOIN payments ON payments.sale_id = sales.id
            JOIN payment_types ON payments.payment_type_id = payment_types.id
        """,
        "depends_on": [],
        "type": JoinType.LEFT,
    },
}


METRICS = {
    "total_vendas": {
        "sql": "SUM(sales.total_amount)",
        "label": "Total de Vendas (Líquido)",
        "type": "currency",
    },
    "ticket_medio": {
        "sql": "AVG(sales.total_amount)",
        "label": "Ticket Médio (Líquido)",
        "type": "currency",
    },
    "total_bruto_itens": {
        "sql": "SUM(sales.total_amount_items)",
        "label": "Total Bruto (Itens)",
        "type": "currency",
    },
    "total_descontos": {
        "sql": "SUM(sales.total_discount)",
        "label": "Total de Descontos (Venda)",
        "type": "currency",
    },
    "total_acrescimos": {
        "sql": "SUM(sales.total_increase)",
        "label": "Total de Acréscimos (Venda)",
        "type": "currency",
    },
    "total_taxa_entrega": {
        "sql": "SUM(sales.delivery_fee)",
        "label": "Total Taxa de Entrega (Venda)",
        "type": "currency",
    },
    "total_taxa_servico": {
        "sql": "SUM(sales.service_tax_fee)",
        "label": "Total Taxa de Serviço",
        "type": "currency",
    },
    "total_pago_cliente": {
        "sql": "SUM(sales.value_paid)",
        "label": "Total Pago pelo Cliente",
        "type": "currency",
    },
    "total_pedidos": {
        "sql": "COUNT(DISTINCT sales.id)",
        "label": "Total de Pedidos",
        "type": "number",
    },
    "total_pessoas_atendidas": {
        "sql": "SUM(sales.people_quantity)",
        "label": "Total de Pessoas Atendidas",
        "type": "number",
    },
    "tempo_medio_preparo_min": {
        "sql": "AVG(sales.production_seconds) / 60.0",
        "label": "T. Médio de Preparo (min)",
        "type": "number",
    },
    "tempo_medio_entrega_min": {
        "sql": "AVG(sales.delivery_seconds) / 60.0",
        "label": "T. Médio de Entrega (min)",
        "type": "number",
    },
    "total_produtos_vendidos": {
        "sql": "SUM(product_sales.quantity)",
        "label": "Total de Produtos Vendidos",
        "joins_needed": ["product_sales"],
        "type": "number",
    },
}


DIMENSIONS = {
    "data_venda": {
        "sql": "DATE_TRUNC('day', sales.created_at)",
        "label": "Data da Venda",
    },
    "hora_venda": {
        "sql": "EXTRACT(HOUR FROM sales.created_at)",
        "label": "Hora da Venda",
    },
    "dia_da_semana": {
        "sql": "EXTRACT(DOW FROM sales.created_at)",
        "label": "Dia da Semana",
    },
    "mes_venda": {
        "sql": "DATE_TRUNC('month', sales.created_at)",
        "label": "Mês da Venda",
    },
    "ano_venda": {
        "sql": "DATE_TRUNC('year', sales.created_at)",
        "label": "Ano da Venda",
    },
    "status_venda": {
        "sql": "sales.sale_status_desc",
        "label": "Status da Venda",
    },
    "origem_venda": {
        "sql": "sales.origin",
        "label": "Origem da Venda",
    },
    "loja_nome": {
        "sql": "stores.name",
        "label": "Nome da Loja",
        "joins_needed": ["stores"],
    },
    "loja_cidade": {
        "sql": "stores.city",
        "label": "Cidade da Loja",
        "joins_needed": ["stores"],
    },
    "loja_estado": {
        "sql": "stores.state",
        "label": "Estado da Loja",
        "joins_needed": ["stores"],
    },
    "loja_bairro": {
        "sql": "stores.district",
        "label": "Bairro da Loja",
        "joins_needed": ["stores"],
    },
    "loja_propria": {
        "sql": "stores.is_own",
        "label": "Loja Própria?",
        "joins_needed": ["stores"],
    },
    "marca_nome": {"sql": "brands.name", "label": "Marca", "joins_needed": ["brands"]},
    "sub_marca_nome": {
        "sql": "sub_brands.name",
        "label": "Sub-marca",
        "joins_needed": ["sub_brands"],
    },
    "canal_nome": {
        "sql": "channels.name",
        "label": "Canal",
        "joins_needed": ["channels"],
    },
    "canal_tipo": {
        "sql": "channels.type",
        "label": "Tipo de Canal",
        "joins_needed": ["channels"],
    },
    "produto_nome": {
        "sql": "products.name",
        "label": "Produto",
        "joins_needed": ["products"],
    },
    "categoria_produto": {
        "sql": "categories.name",
        "label": "Categoria",
        "joins_needed": ["categories"],
    },
    "addon_nome": {
        "sql": "items.name",
        "label": "Addon (Item)",
        "joins_needed": ["items"],
    },
    "addon_grupo": {
        "sql": "option_groups.name",
        "label": "Grupo de Addon",
        "joins_needed": ["option_groups"],
    },
    "cliente_genero": {
        "sql": "customers.gender",
        "label": "Gênero do Cliente",
        "joins_needed": ["customers"],
    },
}
