import duckdb

#caminho do arquivo gerado
caminho_arquivo = 'data_lake_local/bronze_raw/siape_ativos/year=2025/month=01/part-000.parquet'

#SQL
query = f"""
    SELECT *
    FROM '{caminho_arquivo}'
    LIMIT 5
"""

#executa e mostra na tela
resultado = duckdb.sql(query)
print(resultado)