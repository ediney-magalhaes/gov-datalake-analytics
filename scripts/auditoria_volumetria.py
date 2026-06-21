import os
import gcsfs
import pyarrow.parquet as pq
import sys
from dotenv import load_dotenv

load_dotenv()

nome_asset = sys.argv[1]

destino_bronze = os.environ["DESTINO_BRONZE"]

bucket_path = destino_bronze.removeprefix("gs://")

caminho_asset = f"{bucket_path}/bronze_normalized/{nome_asset}/**/*.parquet"

# conectar o GCP e listar arquivos (objeto de conexão)
fs = gcsfs.GCSFileSystem()

lista_arquivos = fs.glob(caminho_asset)
print(f"Arquivos encontrados: {len(lista_arquivos)}")

total_registros = 0
total_bytes = 0

for arquivo in lista_arquivos:
    # dicionário com metadados do arquivo no GCS
    info = fs.info(arquivo)
    total_bytes += info["size"]
    # abre o arquivo remoto
    with fs.open(arquivo) as f:
        # lê só o cabeçalho do Parquet
        metadata = pq.ParquetFile(f).metadata
        # guarda quantidade de linhas (registros) do arquivo
        total_registros += metadata.num_rows

total_gb = total_bytes / (1024 ** 3)

print(f"Total de registros: {total_registros:,}")
print(f"Total em GB: {total_gb:.2F} GB")