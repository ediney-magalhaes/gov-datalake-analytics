"""
Script de correção pontual (one-off) — 07/08/2026.
Corrige inconsistência de tipo (INT64 vs STRING) entre partições Parquet
da fonte enap_capacitacao, causada por inferência de schema do Polars
sem schema_overrides na ingestão original (ver dagster_pipelines/assets/bronze/enap.py).
Não deve ser executado novamente, salvo reincidência do mesmo bug.
"""

import pyarrow.parquet as pq
import pyarrow.compute as pc
import gcsfs
from dotenv import load_dotenv

load_dotenv()

fs = gcsfs.GCSFileSystem()
prefixo = "gov-datalake-analytics-bronze/bronze_normalized/enap_capacitacao/"
arquivos = fs.glob(f"{prefixo}year=*/month=*/*.parquet")

for caminho in arquivos:
    with fs.open(caminho, "rb") as f:
        tabela = pq.read_table(f)

    for coluna in ["idade", "carga_horaria"]:
        if coluna in tabela.column_names:
            indice = tabela.column_names.index(coluna)
            tabela = tabela.set_column(
                indice, coluna, pc.cast(tabela.column(coluna), "string")
            )

    with fs.open(caminho, "wb") as f:
        pq.write_table(tabela, f)

print(f"{len(arquivos)} arquivos corrigidos.")