# ADR-011: dbt Core como motor de transformação

**Data:** 18 de Abril de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Contexto
O projeto necessita de um motor de transformação para construir as camadas Silver e Gold a partir da Bronze Normalized. A ferramenta precisa ser gratuita, versionável em Git, suportar testes de qualidade automatizados e gerar documentação de linhagem de dados.

## Decisão
Adotar o dbt Core (versão open source) como motor oficial de transformação SQL para as camadas Silver e Gold, executado localmente apontando para o BigQuery como destino.

## Alternativas consideradas

- **SQL puro diretamente no BigQuery:** Rejeitado. Sem versionamento, sem testes automatizados e sem documentação de linhagem.

- **Dataform (Google):** Rejeitado. Ferramenta SaaS dependente do Google Cloud Console — menor controle sobre o código e versionamento menos flexível que o dbt com Git.

- **Spark / PySpark:** Rejeitado. Complexidade e infraestrutura desnecessárias para o volume do projeto. Custo de cluster incompatível com a premissa de custo zero.

## Consequências

**Positivas:**
- Transformações versionadas em Git — rastreabilidade total
- Testes de qualidade nativos (unique, not_null, accepted_values)
- Documentação de linhagem gerada automaticamente via dbt docs
- Desenvolvimento local com DuckDB antes do deploy no BigQuery

**Negativas / Trade-offs:**
- Curva de aprendizado do paradigma SQL-first do dbt
- Requer reescrita dos modelos Silver e Gold existentes para incorporar as novas fontes da Fase 1

**Dependência:**
- A reconstrução dos modelos dbt (Fase 5) só pode iniciar após a conclusão da Bronze Normalized de todas as fontes e a 
  promoção da ADR-009 para "Aceito"