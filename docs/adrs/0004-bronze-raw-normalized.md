# ADR-004 — Divisão da Camada Bronze em Raw e Normalized
**Data:** 2026-03-07  
**Status:** Aceito  
**Decisores:** Ediney Magalhães (Arquiteto de Dados / Lead Data Engineer)

## Contexto
O projeto passou de uma Prova de Conceito (PoC) para uma Plataforma de Dados Governamental, com a necessidade de ingerir 6 sistemas estruturantes simultâneos (SIAPE, SIAPEcad, SIGEPE, SouGov, Vozes, DEPRO) contendo mais de 10 anos de histórico.
A ingestão heterogênea dessas fontes diretamente para consumo no dbt (Camada Prata) geraria um custo altíssimo de processamento (scans) no BigQuery e transformaria a camada analítica em um gargalo de "higiene estrutural".

## Decisão
Dividir logicamente a Camada Bronze no Data Lake em duas zonas:
1. **Bronze Raw:** Focada em persistência imutável, particionada e 100% fiel à origem (backup de auditoria), com aplicação apenas de pseudonimização in-flight (LGPD).
2. **Bronze Normalized:** Focada em padronização estrutural universal (snake_case, tipagem básica, adição de metadados de linhagem como `ingestion_timestamp` e harmonização da chave `hash_cpf`).

## Alternativas consideradas
- **Tratar tudo na Camada Prata (dbt):** Rejeitado. Isso obrigaria o BigQuery a ler dados brutos e despadronizados repetidas vezes, aumentando o custo financeiro (FinOps) e poluindo a modelagem de negócios com regras de limpeza de strings e datas.
- **Tratar tudo na extração (Pipeline Python):** Rejeitado. Feriria o princípio de evidência. Precisamos do dado "sujo" original guardado caso as regras de negócio mudem no futuro.

## Consequências
Benefícios:
- A camada Prata (Silver) foca 100% em regras de negócio e cruzamentos.
- Redução de custos no Data Warehouse (a limpeza pesada ocorre mais barata na Bronze).
- Harmonização universal de chaves para facilitar JOINs futuros.

Trade-offs:
- Aumento do volume de armazenamento no Data Lake (teremos o dado duas vezes na Bronze: Raw e Normalized), o que é aceitável visto o baixo custo de storage em nuvem.

## Validação
- Os pipelines de ingestão devem salvar primeiramente no path `bronze_raw/`.
- Um job subsequente deve ler da `bronze_raw/`, padronizar e salvar em `bronze_normalized/`.