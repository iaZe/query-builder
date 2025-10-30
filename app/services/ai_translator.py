import httpx
import logging
import json
from app.services.semantic_layer import METRICS, DIMENSIONS

SIMPLE_METRICS = {k: v["label"] for k, v in METRICS.items()}
SIMPLE_DIMENSIONS = {k: v["label"] for k, v in DIMENSIONS.items()}

SYSTEM_PROMPT = f"""
Você é um assistente de analytics para donos de restaurante. Sua *única* função é 
traduzir o pedido do usuário em um JSON formatado para uma API.

REGRAS ESTRICTAS:
1. Responda *apenas* com o JSON. NUNCA use texto explicativo, saudações ou markdown (```json).
2. Use *apenas* as chaves de métricas e dimensões fornecidas abaixo.
3. Se o usuário pedir por "vendas", "faturamento" ou "dinheiro", use a métrica "total_vendas".
4. Se o usuário pedir "top 3", "5 mais", etc., use "order_by" e "limit".
5. Se o usuário não especificar uma métrica, use "total_vendas" como padrão.
6. Se o usuário não especificar dimensões, use uma lista vazia [].

---
CHAVES DE MÉTRICAS DISPONÍVEIS (Use a chave, não a label):
{json.dumps(SIMPLE_METRICS, indent=2, ensure_ascii=False)}
---
CHAVES DE DIMENSÕES DISPONÍVEIS (Use a chave, não a label):
{json.dumps(SIMPLE_DIMENSIONS, indent=2, ensure_ascii=False)}
---

EXEMPLOS:

Usuário: "Quero saber os 3 produtos mais vendidos no iFood"
JSON:
{{
  "metrics": ["total_vendas"],
  "dimensions": ["produto_nome"],
  "filters": [
    {{"field": "canal_nome", "operator": "eq", "value": "iFood"}}
  ],
  "order_by": [
    {{"field": "total_vendas", "direction": "desc"}}
  ],
  "limit": 3
}}

Usuário: "Qual o ticket médio por método de pagamento, apenas para pedidos cancelados?"
JSON:
{{
  "metrics": ["ticket_medio"],
  "dimensions": ["metodo_pagamento"],
  "filters": [
    {{"field": "status_venda", "operator": "eq", "value": "Cancelada"}}
  ],
  "order_by": [],
  "limit": 100
}}

Usuário: "Faturamento total"
JSON:
{{
  "metrics": ["total_vendas"],
  "dimensions": [],
  "filters": [],
  "order_by": [],
  "limit": 1
}}
"""


class AITranslator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://chat.maritaca.ai/api/chat/inference"

    async def generate_query_json(self, user_prompt: str) -> str:
        """
        Chama a API da Maritaca AI para traduzir o texto em JSON.
        """
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "sabia-3",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "do_sample": False,
            "max_tokens": 1024,
            "temperature": 0.0,
            "top_p": 0.1,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url, json=payload, headers=headers, timeout=30.0
                )
                response.raise_for_status()

                data = response.json()

                json_output = data["answer"]

                json_output = (
                    json_output.strip()
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

                return json_output

            except httpx.HTTPStatusError as e:
                logging.error(
                    f"Erro da API Maritaca ({e.response.status_code}): {e.response.text}"
                )
                raise Exception(f"Erro na API da IA: {e.response.status_code}")
            except Exception as e:
                logging.error(f"Erro ao chamar AITranslator: {e}")
                raise e
