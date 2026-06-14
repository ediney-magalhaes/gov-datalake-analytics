# ADR-015 — Motor de Ingestão Próprio com Polars e Requests

**Data:** 2026-06-13

**Status:** Aceito

**Decisores:** Ediney Magalhães (Data Engineer)

---

## Contexto

A decisão original (ADR-003) previa o uso do framework dlt (Data Load Tool) para extração resiliente de APIs governamentais. Durante a análise das fontes de dados, identificou-se que as APIs estruturadas do governo federal (SIAPE, DEPRO, SIGEPE, SouGov) exigem autenticação via chave de API institucional, à qual a consultoria não possui acesso direto.

As bases necessárias estão disponíveis exclusivamente via download de arquivos compactados (ZIP e TAR.GZ) no Portal da Transparência — um modelo de distribuição em lote, não via API paginada. O dlt é otimizado para extração de APIs REST com paginação e autenticação, tornando-o inadequado para esse padrão de acesso.

---

## Decisão

Abandonar o dlt e construir um **motor de ingestão próprio**, composto por:

- **Requests** — download HTTP dos arquivos compactados com headers dinâmicos para evasão de WAF governamental
- **Polars (Apache Arrow)** — leitura e processamento in-memory dos CSVs extraídos (ADR-001)
- **gcsfs** — escrita direta dos arquivos Parquet no Google Cloud Storage (ADR-014)
- **hashlib** — pseudonimização SHA-256 + Salt in-flight (ADR-013)
- **python-dotenv** — gerenciamento de variáveis de ambiente como contrato de configuração

O motor é implementado em `dagster_pipelines/resources/motor_ingestao.py` e expõe duas funções reutilizáveis por todos os assets:

- `ingestao_bronze_raw_zip()` — download, extração, pseudonimização e escrita na Bronze Raw
- `normalizacao_da_bronze_raw()` — leitura da Bronze Raw, padronização snake_case, injeção de metadados e escrita na Bronze Normalized

---

## Alternativas consideradas

- **dlt:** inadequado — exige APIs autenticadas com paginação; as fontes disponíveis são arquivos em lote via Portal da Transparência.
- **Airbyte/Fivetran:** dependência de SaaS, custo elevado e menor controle sobre pseudonimização LGPD in-flight.
- **Script manual por fonte:** aumenta duplicidade de código e dificulta manutenção e padronização entre os 8 assets.

---

## Consequências

Benefícios:
- controle total sobre o fluxo de extração, pseudonimização e persistência
- motor reutilizável por todos os assets via parâmetros configuráveis
- sem dependência de chaves de API institucionais
- pseudonimização LGPD aplicada in-flight, antes de qualquer persistência

Trade-offs:
- responsabilidade de manutenção do motor recai inteiramente sobre a consultoria
- resiliência a falhas (retry, idempotência granular por etapa) precisa ser implementada manualmente

Riscos:
- instabilidade do Portal da Transparência (rate limit, bloqueios 403, mudanças de URL) impacta diretamente o pipeline — mitigado via headers dinâmicos e tratamento de exceções
- mudanças de schema nas origens (contract drift) requerem monitoramento ativo — planejado para Fase 2

---

## Validação

- execução bem-sucedida de backfill histórico completo do SIAPE Ativos (132 partições, 100.659.967 registros, 6,90 GB)
- escrita validada em `bronze_raw` e `bronze_normalized` no GCS
- pseudonimização confirmada — nenhum CPF em texto claro persistido