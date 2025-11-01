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
    "item_product_sales": {
        "sql": "LEFT JOIN item_product_sales ON item_product_sales.product_sale_id = product_sales.id",
        "depends_on": ["product_sales"],
        "type": JoinType.LEFT,
    },
    "items": {
        "sql": "LEFT JOIN items ON item_product_sales.item_id = items.id",
        "depends_on": ["item_product_sales"],
        "type": JoinType.LEFT,
    },
    "option_groups": {
        "sql": "LEFT JOIN option_groups ON item_product_sales.option_group_id = option_groups.id",
        "depends_on": ["item_product_sales"],
        "type": JoinType.LEFT,
    },
    "brands": {
        "sql": "LEFT JOIN brands ON stores.brand_id = brands.id",
        "depends_on": ["stores"],
        "type": JoinType.LEFT,
    },
    "sub_brands": {
        "sql": "LEFT JOIN sub_brands ON stores.sub_brand_id = sub_brands.id",
        "depends_on": ["stores"],
        "type": JoinType.LEFT,
    },
    "payments": {
        "sql": "LEFT JOIN payments ON payments.sale_id = sales.id",
        "depends_on": [],
        "type": JoinType.LEFT,
    },
    "payment_types": {
        "sql": "LEFT JOIN payment_types ON payments.payment_type_id = payment_types.id",
        "depends_on": ["payments"],
        "type": JoinType.LEFT,
    },
    "coupon_sales": {
        "sql": "LEFT JOIN coupon_sales ON coupon_sales.sale_id = sales.id",
        "depends_on": [],
        "type": JoinType.LEFT,
    },
    "coupons": {
        "sql": "LEFT JOIN coupons ON coupon_sales.coupon_id = coupons.id",
        "depends_on": ["coupon_sales"],
        "type": JoinType.LEFT,
    },
    "delivery_sales": {
        "sql": "LEFT JOIN delivery_sales ON delivery_sales.sale_id = sales.id",
        "depends_on": [],
        "type": JoinType.LEFT,
    },
    "delivery_addresses": {
        "sql": "LEFT JOIN delivery_addresses ON delivery_addresses.sale_id = sales.id",
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
    "total_addons_vendidos": {
        "sql": "SUM(item_product_sales.quantity)",
        "label": "Total de Addons Vendidos",
        "joins_needed": ["item_product_sales"],
        "type": "number",
    },
    "receita_total_addons": {
        "sql": "SUM(item_product_sales.additional_price)",
        "label": "Receita Total de Addons",
        "joins_needed": ["item_product_sales"],
        "type": "currency",
    },
    "total_processado_pagamentos": {
        "sql": "SUM(payments.value)",
        "label": "Total Processado (Pagamentos)",
        "joins_needed": ["payments"],
        "type": "currency",
    },
    "total_desconto_cupom": {
        "sql": "SUM(coupon_sales.value)",
        "label": "Total Desconto (Cupons)",
        "joins_needed": ["coupon_sales"],
        "type": "currency",
    },
    "total_cupons_usados": {
        "sql": "COUNT(DISTINCT coupon_sales.id)",
        "label": "Total de Cupons Usados",
        "joins_needed": ["coupon_sales"],
        "type": "number",
    },
    "total_custo_entregador": {
        "sql": "SUM(delivery_sales.courier_fee)",
        "label": "Custo Total (Entregador)",
        "joins_needed": ["delivery_sales"],
        "type": "currency",
    },
}


DIMENSIONS = {
    "data_venda": {
        "sql": "DATE_TRUNC('day', sales.created_at)",
        "label": "Data da Venda",
        "type": "time",
    },
    "hora_venda": {
        "sql": "EXTRACT(HOUR FROM sales.created_at)",
        "label": "Hora da Venda",
        "type": "category",
    },
    "dia_da_semana": {
        "sql": "EXTRACT(DOW FROM sales.created_at)",
        "label": "Dia da Semana",
        "type": "category",
    },
    "mes_venda": {
        "sql": "DATE_TRUNC('month', sales.created_at)",
        "label": "Mês da Venda",
        "type": "time",
    },
    "ano_venda": {
        "sql": "DATE_TRUNC('year', sales.created_at)",
        "label": "Ano da Venda",
        "type": "time",
    },
    "status_venda": {
        "sql": "sales.sale_status_desc",
        "label": "Status da Venda",
        "type": "category",
    },
    "origem_venda": {
        "sql": "sales.origin",
        "label": "Origem da Venda",
        "type": "category",
    },
    "loja_nome": {
        "sql": "stores.name",
        "label": "Nome da Loja",
        "joins_needed": ["stores"],
        "type": "category",
    },
    "loja_cidade": {
        "sql": "stores.city",
        "label": "Cidade da Loja",
        "joins_needed": ["stores"],
        "type": "geographic",
    },
    "loja_estado": {
        "sql": "stores.state",
        "label": "Estado da Loja",
        "joins_needed": ["stores"],
        "type": "geographic",
    },
    "loja_bairro": {
        "sql": "stores.district",
        "label": "Bairro da Loja",
        "joins_needed": ["stores"],
        "type": "geographic",
    },
    "loja_propria": {
        "sql": "stores.is_own",
        "label": "Loja Própria?",
        "joins_needed": ["stores"],
        "type": "category",
    },
    "marca_nome": {
        "sql": "brands.name",
        "label": "Marca",
        "joins_needed": ["brands"],
        "type": "category",
    },
    "sub_marca_nome": {
        "sql": "sub_brands.name",
        "label": "Sub-marca",
        "joins_needed": ["sub_brands"],
        "type": "category",
    },
    "canal_nome": {
        "sql": "channels.name",
        "label": "Canal",
        "joins_needed": ["channels"],
        "type": "category",
    },
    "canal_tipo": {
        "sql": "channels.type",
        "label": "Tipo de Canal",
        "joins_needed": ["channels"],
        "type": "category",
    },
    "produto_nome": {
        "sql": "products.name",
        "label": "Produto",
        "joins_needed": ["products"],
        "type": "category",
    },
    "categoria_produto": {
        "sql": "categories.name",
        "label": "Categoria",
        "joins_needed": ["categories"],
        "type": "category",
    },
    "addon_nome": {
        "sql": "items.name",
        "label": "Addon (Item)",
        "joins_needed": ["items"],
        "type": "category",
    },
    "addon_grupo": {
        "sql": "option_groups.name",
        "label": "Grupo de Addon",
        "joins_needed": ["option_groups"],
        "type": "category",
    },
    "cliente_genero": {
        "sql": "customers.gender",
        "label": "Gênero do Cliente",
        "joins_needed": ["customers"],
        "type": "category",
    },
    "cliente_origem_cadastro": {
        "sql": "customers.registration_origin",
        "label": "Origem do Cadastro",
        "joins_needed": ["customers"],
        "type": "category",
    },
    "metodo_pagamento": {
        "sql": "payment_types.description",
        "label": "Método de Pagamento",
        "joins_needed": ["payment_types"],
        "type": "category",
    },
    "pagamento_online": {
        "sql": "payments.is_online",
        "label": "Pagamento Online?",
        "joins_needed": ["payments"],
        "type": "category",
    },
    "cupom_codigo": {
        "sql": "coupons.code",
        "label": "Código do Cupom",
        "joins_needed": ["coupons"],
        "type": "string",
    },
    "cupom_tipo_desconto": {
        "sql": "coupons.discount_type",
        "label": "Tipo de Desconto (Cupom)",
        "joins_needed": ["coupons"],
        "type": "category",
    },
    "entregador_nome": {
        "sql": "delivery_sales.courier_name",
        "label": "Entregador",
        "joins_needed": ["delivery_sales"],
        "type": "string",
    },
    "entregue_por": {
        "sql": "delivery_sales.delivered_by",
        "label": "Entregue Por",
        "joins_needed": ["delivery_sales"],
        "type": "category",
    },
    "tipo_entrega": {
        "sql": "delivery_sales.delivery_type",
        "label": "Tipo de Veículo (Entrega)",
        "joins_needed": ["delivery_sales"],
        "type": "category",
    },
    "bairro_entrega": {
        "sql": "delivery_addresses.neighborhood",
        "label": "Bairro de Entrega",
        "joins_needed": ["delivery_addresses"],
        "type": "geographic",
    },
    "cidade_entrega": {
        "sql": "delivery_addresses.city",
        "label": "Cidade de Entrega",
        "joins_needed": ["delivery_addresses"],
        "type": "geographic",
    },
}
