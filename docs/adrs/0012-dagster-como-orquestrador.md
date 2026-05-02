# ADR-012: Dagster como orquestrador de pipelines

**Data:** 18 de Abril de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Contexto
O projeto possui múltiplos pipelines de ingestão (6+ fontes) e transformação (dbt) que precisam ser executados em ordem, com dependências entre si, retries automáticos e agendamento mensal. A execução manual via terminal é inviável em produção e não atende aos requisitos de rastreabilidade e governança operacional.

## Decisão
Adotar o Dagster como orquestrador oficial de pipelines, substituindo a execução manual do executar_ingestao.py e integrando os assets de ingestão (Polars/dlt) com os modelos 
de transformação (dbt Core).

## Alternativas consideradas
- **Apache Airflow:** Rejeitado. Infraestrutura pesada — requer servidor dedicado ou serviço gerenciado. Incompatível com a premissa de custo zero e com o hardware atual (8 GB RAM).

- **Prefect:** Rejeitado. Cloud-first — a versão gratuita tem limitações de execuções mensais que podem comprometer o backfill de 10 anos de histórico.

- **Mage.ai:** Rejeitado. Menos maduro para pipelines de dados governamentais complexos com múltiplas dependências entre fontes heterogêneas.

- **Cron + scripts Python:** Rejeitado. Sem gerenciamento de dependências, sem retry automático, sem observabilidade e sem interface de monitoramento — inaceitável para auditoria.

## Consequências
**Positivas:**
- Interface web local para monitoramento de execuções
- Gerenciamento nativo de dependências entre assets
- Retry automático para APIs instáveis do Governo
- Backfill de histórico gerenciado sem intervenção manual
- Integração nativa com dbt Core

**Negativas / Trade-offs:**
- Curva de aprendizado do paradigma de assets do Dagster
- Migração do executar_ingestao.py atual para o modelo de assets requer refatoração dos scripts existentes

**Nota:**
- Originalmente planejado para Fase 3, implementado na Fase 1 por decisão arquitetural — a reestruturação em assets Dagster foi feita durante a ingestão para evitar retrabalho.