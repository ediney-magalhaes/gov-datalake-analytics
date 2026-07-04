import os
import requests
import polars as pl
import gcsfs
import tarfile
import logging
import hashlib
from dotenv import load_dotenv
from dagster import asset, MonthlyPartitionsDefinition
from dagster_pipelines.resources.motor_ingestao import normalizacao_da_bronze_raw

load_dotenv()

# função para carregar arquivo
def garantir_cache_enap():
    cache_local = os.getenv("CACHE_LOCAL")
    url_enap = os.getenv("ENAP_URL_BASE_COMPLETA")
    caminho = os.path.join(cache_local, os.path.basename(url_enap).replace(".tar.gz", ".csv"))
    caminho_tar = os.path.join(cache_local, os.path.basename(url_enap))
    if os.path.exists(caminho):
        return caminho
    elif os.path.exists(caminho_tar):
        # extrair o csv
        with tarfile.open(caminho_tar, "r:gz") as tar:
            tar.extractall(cache_local)
    else:
        resposta = requests.get(url_enap, stream=True)        
        # escrever o arquivo em disco
        with open(caminho_tar, "wb") as f:
            for pedaco in resposta.iter_content(chunk_size=8192):
                f.write(pedaco)
        # extrair o csv
        with tarfile.open(caminho_tar, "r:gz") as tar:
            tar.extractall(cache_local)
    return caminho


# Definição da partição mensal — de janeiro/2015 até o mês atual
particao_mensal = MonthlyPartitionsDefinition(start_date="2015-01-01")

# Asset: enap_capacitacao
# O que faz: Baixa os dados de capacitação da Escola Virtual Gov e salva como Parquet particionado por ano/mês
# Partição: Mensal (2015-01 até o mês atual)
# Fonte: TAR.GZ público da Escola Virtual Gov (dupla compactação: TAR.GZ > TAR.GZ > CSV)
# Arquivo interno: {ano}_{mes}_escolavirtual_dadosabertos_matriculas_utf8.tar.gz > .csv
# Separador: | (pipe)
# Encoding: utf-8
@asset(group_name="bronze_enap", partitions_def=particao_mensal)
def enap_capacitacao(context):
    """Matrículas e capacitação de servidores — Escola Virtual Gov — Bronze Raw e Normalized"""
    chave = context.partition_key
    ano = chave[:4]
    mes = chave[5:7]
    caminho_csv = garantir_cache_enap()
    df = pl.scan_csv(caminho_csv, separator="|").filter(
        (pl.col("dt_inicio").str.to_datetime("%Y-%m-%d %H:%M:%S").dt.year() == int(ano)) & (pl.col("dt_inicio").str.to_datetime("%Y-%m-%d %H:%M:%S").dt.month() == int(mes))
        ).collect()
    
    # leitura de hash
    salt = os.getenv("HASH_SALT")

    # verifica se existe CPF
    if "CPF" in df.columns:
        df = df.with_columns(
            pl.col("CPF").map_elements(lambda x: hashlib.sha256((str(x) + str(salt)).encode('utf-8')).hexdigest(), return_dtype=pl.String).alias("hash_cpf")
        )
        # remove a coluna de CPF
        df = df.drop("CPF")

    
    destino = os.getenv("DESTINO_BRONZE")
    caminho_gcs = f'{destino}/bronze_raw/enap_capacitacao/year={ano}/month={mes}/part-000.parquet'
    # verificação de idempotência
    if caminho_gcs.startswith("gs://"):
        fs = gcsfs.GCSFileSystem()
        if fs.exists(caminho_gcs):
            logging.info(f'Raw já existe para Enap Capacitação: {ano}/{mes}!')
            return
    # salvar df como arquivo parquet no GCS
    df.write_parquet(caminho_gcs)

    normalizacao_da_bronze_raw(sistema='enap_capacitacao', ano=ano, mes=mes)
