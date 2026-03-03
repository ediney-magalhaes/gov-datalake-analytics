# ADR-002 — Persistência física da Bronze em Parquet antes do Data Warehouse

**Data:** 2026-02-25  

**Status:** Aceito  

**Decisores:** Ediney Magalhães (Data Engineer)



## Contexto

A ingestão direta para o Data Warehouse (BigQuery) sem uma camada física imutável:

- reduz rastreabilidade operacional

- dificulta rollback e auditoria

- aumenta dependência do DW como “único storage”

- limita estratégia Lakehouse futura



## Decisão

Persistir a Camada Bronze como **Parquet (colunar) em filesystem/cloud storage**, funcionando como backup imutável e camada raw.



## Alternativas consideradas

- **Somente BigQuery (raw no DW):** simples, mas acopla ingestão à nuvem e dificulta reprocessamento seguro.

- **CSV bruto em disco:** custo maior, pouco eficiente, sem compressão e ruim para leitura analítica.

- **Avro/JSON:** menos eficiente para analytics; maior overhead.



## Consequências

Benefícios:

- camada raw imutável auditável

- compressão e performance de leitura

- habilita evolução para Lakehouse



Trade-offs:

- gerenciamento de diretórios/partições Parquet

- política de retenção e versionamento do lake



Riscos:

- necessidade de garantir nomenclatura/particionamento consistente



## Validação

- verificar reprocessamento a partir dos Parquets sem depender da origem

- validar volume e checksums por partição/mês

- medir ganho de custo e tempo em reload



---