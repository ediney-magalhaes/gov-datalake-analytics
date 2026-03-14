# ADR 0008: Desativação de Inferência de Schema na Camada Bronze Raw

**Data:** 14 de Março de 2026
**Status:** Aceito
**Autor:** Ediney Magalhães

## Contexto
Durante a ingestão massiva de arquivos públicos (ex: Portal da Transparência - SIAPE Remuneração), o motor Polars apresentou falhas de parse (`ComputeError`). A investigação revelou que o Governo Federal insere textos explicativos e notas de rodapé (ex: `(*) Verbas indenizatórias...`) nas últimas linhas dos arquivos CSV. Como o Polars infere o tipo da coluna com base nas primeiras linhas, ele assume que colunas numéricas (como 'ANO') são inteiros (`i64`) e "quebra" ao encontrar o texto no rodapé.

## Decisão
Fica estabelecido que o motor de extração genérico da camada bruta (`pipeline_bronze_raw_polars.py`) deve ler **todas as colunas estritamente como Texto (String)**, utilizando o parâmetro `infer_schema_length=0`.
A responsabilidade de tipagem (Casting para Inteiros, Datas, Floats) é totalmente removida da ingestão física (Raw) e delegada para a etapa de transformação (Camada Silver com dbt) ou para regras específicas na Bronze Normalized.

## Consequências
* **Positivas:** Resiliência extrema do pipeline. O motor engole qualquer CSV governamental sem quebrar, garantindo que o dado chegue ao Data Lake.
* **Negativas:** Os arquivos Parquet na `bronze_raw` ocuparão levemente mais espaço em disco e memória temporária, pois números estarão salvos como texto bruto.