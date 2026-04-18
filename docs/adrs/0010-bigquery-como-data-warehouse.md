# ADR-010: BigQuery como Data Warehouse das camadas Silver e Gold

**Data:** 18 de Abril de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Contexto
O projeto necessita de um Data Warehouse para hospedar as camadas Silver e Gold. A escolha precisa atender à premissa de custo zero ou mínimo, suportar consultas SQL analíticas complexas, integrar com o Power BI e ser acessível por múltiplos usuários remotamente.

## Decisão
Adotar o Google BigQuery como Data Warehouse oficial das camadas Silver e Gold, utilizando exclusivamente o free tier:
- 10 GB de storage gratuito permanente
- 1 TB de queries gratuitas por mês
- As tabelas Silver e Gold são mantidas dentro do limite de 10 GB pois são agregações da Bronze, não cópias completas

## Alternativas consideradas
- **DuckDB local como DW principal:** Rejeitado para produção. Com 8 GB de RAM e 13,9 GB livres em disco, o hardware atual não suporta o volume estimado de centenas de gigabytes do histórico completo. DuckDB permanece como ferramenta de desenvolvimento e testes locais.

- **Snowflake:** Rejeitado. Free tier limitado a 30 dias — inviável para um projeto de longa duração com premissa de custo zero.

- **PostgreSQL (Cloud SQL):** Rejeitado. Banco OLTP, não OLAP. Performance inadequada para queries analíticas em grandes volumes e custo de instância contínua.

## Consequências
**Positivas:**
- Custo zero dentro do free tier para o volume estimado do projeto
- Integração nativa com Power BI, GCS e dbt Core
- Acesso remoto multiusuário sem infraestrutura adicional
- SQL padrão com suporte a particionamento e clustering para FinOps

**Negativas / Trade-offs:**
- Dependência de conectividade com internet para queries
- Risco de custo se queries mal otimizadas escanearem além do free tier — mitigado pela Fase 4.1 (External Tables) e pelas boas práticas de particionamento e clustering

**Decisão complementar:**
A Fase 4.1 define a estratégia de External Tables, que permite ao BigQuery ler diretamente do Parquet no GCS sem duplicar storage — decisão que deve preceder a construção das camadas Silver e Gold.