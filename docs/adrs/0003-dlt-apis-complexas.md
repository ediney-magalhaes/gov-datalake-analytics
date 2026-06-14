# ADR-003 — Extração de APIs complexas com dlt para resiliência e padronização

**Data:** 2026-02-25

**Status:** Superseded — substituído por ADR-001 (Polars in-memory) e ADR-015 (Motor de Ingestão Próprio)  

**Decisores:** Ediney Magalhães (Data Engineer)



## Contexto

APIs governamentais podem apresentar:

- instabilidade, rate limit e bloqueios por WAF (403/timeout)

- necessidade de paginação e retry inteligente

- variação de schema (contract drift)



## Decisão

Adotar o framework **dlt (Data Load Tool)** para padronizar extração, paginação e resiliência de ingestão via API.



## Alternativas consideradas

- **Requests + paginação manual:** aumenta complexidade, difícil padronizar retries e observabilidade.

- **Airbyte/Fivetran:** dependência de SaaS, custo e menor controle fino.

- **Scrapy customizado:** bom para scraping, mas não é o foco para pipelines de dados.



## Consequências

Benefícios:

- padronização de conectores

- resiliência e modularidade

- base pronta para automação futura (DataOps)



Trade-offs:

- aprender convenções do dlt

- integrar logs e tratamento LGPD no fluxo



Riscos:

- versão/compatibilidade de libs pode exigir manutenção



## Validação

- taxa de sucesso de execução em cenários de erro 403/timeout

- logs estruturados por endpoint e partição

- teste de idempotência em reexecuções