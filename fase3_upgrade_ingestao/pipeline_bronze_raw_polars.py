import io
import requests
import zipfile
import polars as pl
import logging
import sys
import hashlib
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()
salt = os.getenv('HASH_SALT')

#preparação do formatador do arquivo de log
formatador = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#log do arquivo
arquivo_log = logging.FileHandler('pipeline_bronze_raw.log', encoding='utf-8')

#log da tela
tela_log = logging.StreamHandler(sys.stdout)

#chamando os logs
arquivo_log.setFormatter(formatador)
tela_log.setFormatter(formatador)

#definindo volume de logs
logging.getLogger().setLevel(logging.INFO)

#conectando os logs a definição de níveis
logging.getLogger().addHandler(arquivo_log)
logging.getLogger().addHandler(tela_log)

#função para ingestão das bases
def ingestao_bronze_raw_zip(sistema, ano, mes, url_download, nome_arquivo_interno):

    #obtendo retorno da url em bytes
    logging.info(f'Iniciando o download dos dados do {sistema} para o periodo {ano}{mes}')
    resposta = requests.get(url_download, verify=False)
    arquivo_zip = io.BytesIO(resposta.content)

    #abrindo o arquivo zip
    with zipfile.ZipFile(arquivo_zip) as z:
        #print(f"\nCONTEÚDO DO ZIP ({sistema}): {z.namelist()}\n")
        #extraindo o arquivo
        arquivo_extraido = z.open(nome_arquivo_interno)

        #lendo o arquivo com o Polars
        df = pl.read_csv(arquivo_extraido.read(), separator=';', encoding='latin1', infer_schema_length=0)
        logging.info(f'Arquivo lido com sucesso pelo Polars. {df.height} linhas encontradas.')

        #adicionando colunas de metadados
        df = df.with_columns(
            pl.lit(sistema).alias('source_system'),
            pl.lit(datetime.now().isoformat()).alias('ingestion_timestamp'),
            pl.lit('v1').alias('schema_version')
        )
        #verificando existencia de CPF na base e aplicando anonimização quando houver
        if 'CPF' in df.columns:
            df = df.with_columns(
                pl.col('CPF').map_elements(lambda x: hashlib.sha256((str(x)+str(salt)).encode('utf-8')).hexdigest(), return_dtype=pl.String).alias('hash_cpf'),
            )
            #excluindo a coluna de CPF por segurança
            df = df.drop('CPF')
            logging.info('Anonimizacao aplicada com sucesso na coluna CPF!')
        else:
            logging.info('Coluna CPF não encontrada. Pulando anonimização.')

        #criando caminho da partição (Bronze Raw)
        caminho_particao = f'data_lake_local/bronze_raw/{sistema}/year={ano}/month={mes}'

        #criando diretorio
        os.makedirs(caminho_particao, exist_ok=True)

        #salvando o arquivo
        df.write_parquet(f'{caminho_particao}/part-000.parquet')
        logging.info('Arquivo salvo com sucesso!')
