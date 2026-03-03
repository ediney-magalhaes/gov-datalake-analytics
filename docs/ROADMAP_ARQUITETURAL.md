# Roadmap Arquitetural — Data Lake Analytics GOV

Este documento define a evolução planejada da arquitetura do projeto, organizando as fases técnicas e as próximas decisões estruturantes.

O objetivo é garantir maturidade progressiva da solução, alinhando:

- Escalabilidade

- Governança

- Conformidade (LGPD)

- Performance

- Sustentabilidade (FinOps)

- Reprodutibilidade (DataOps)


---



## Fase 1 e 2 — Prova de Conceito (Legado)


**Stack:** Pandas + PostgreSQL + BigQuery  

**Status:** Refatorada  


### Entregas:

- Ingestão inicial de arquivos massivos

- Diagnóstico de qualidade de dados

- Primeiras modelagens no BigQuery

- Implementação inicial de dbt


### Limitações identificadas:

- Risco de OOM (Out Of Memory)

- Dependência excessiva de Pandas

- Ausência de persistência física imutável (Lake)

- Logging limitado


---



## Fase 3 — Upgrade de Ingestão (Atual)


**Stack:** Polars + dlt + DuckDB + Parquet  

**Status:** Em execução


### Evoluções Implementadas:


- Substituição de Pandas por **Polars (Apache Arrow)**

- Processamento vetorizado in-memory

- Persistência física em formato **Parquet**

- Introdução do framework **dlt** para ingestão de APIs

- Implementação de **Dual Logging**

- Pseudonimização determinística (SHA-256) in-flight

- Estruturação formal da Camada Bronze como Data Lake


### Objetivo da fase:

Consolidar uma arquitetura resiliente e escalável antes da orquestração.


---


## Fase 4 — Consolidação Cloud (Prata e Ouro)


**Stack:** BigQuery + dbt Core  

**Status:** Concluída


### Entregas:

- Modelagem Staging (Camada Prata)

- Deduplicação técnica via ROW_NUMBER()

- Contratos de dados (dbt tests)

- Data Marts consolidados (Ouro)

- Estratégia FinOps (materialização física)


---


## Fase 5 — Orquestração e DataOps (Planejada)


### Objetivos:


- Implementar orquestração (Airflow ou alternativa)

- Implementar CI/CD via GitHub Actions

- Automatizar execução de dbt test

- Monitoramento automatizado de falhas de ingestão

- Separação de ambientes (dev / prod)


---


## Fase 6 — Observabilidade e FinOps Avançado (Planejada)


### Evoluções Esperadas:


- Monitoramento de custo por dataset no BigQuery

- Implementação de particionamento automático incremental

- Clustering físico otimizado

- Métricas de performance comparativa (antes/depois)

- Monitoramento de qualidade contínuo (Data SLAs)


---


## Fase 7 — Lakehouse e Escala (Visão de Longo Prazo)


- Integração direta Parquet → BigQuery External Tables

- Estratégia híbrida Lake + Warehouse

- Versionamento de datasets (Time Travel / Snapshotting)

- Monitoramento de Data Drift

- Evolução para arquitetura Lakehouse consolidada


---


# Princípios Arquiteturais Norteadores


- Security First (LGPD in-flight)

- ELT como padrão

- Idempotência

- Analytics as Code

- Governança automatizada

- Escalabilidade orientada a custo

- Rastreabilidade ponta a ponta

---