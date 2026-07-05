import io
import os
import re
import requests
import zipfile
import tarfile
import polars as pl
import logging
import hashlib
import gcsfs
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
salt = os.getenv('HASH_SALT')
destino_bronze = os.getenv('DESTINO_BRONZE')

def ingestao_bronze_raw_zip(sistema, ano, mes, url_download, nome_arquivo_interno, separador=';', encoding='latin1', formato_compactado='zip'):
    """Baixa arquivo compactado, extrai CSV, anonimiza CPF e salva como Parquet particionado na Bronze Raw."""
    
    #obtendo retorno da url em bytes
    cabecalho = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Connection': 'keep-alive'
    }
    logging.info(f'Iniciando o download dos dados do {sistema} para o periodo {ano}{mes}')
    resposta = requests.get(url_download, verify=False, headers=cabecalho, timeout=120)

    #verificando o status de resposta
    if resposta.status_code == 404:
        logging.info(f"A partição {ano}/{mes} do sistema {sistema} não esta disponível. Pulando para a próxima partição...")
        return
    
    #abrindo o arquivos conforme formato
    arquivo_bytes = io.BytesIO(resposta.content)
    if formato_compactado == 'zip':
        with zipfile.ZipFile(arquivo_bytes) as z:
            conteudo = z.open(nome_arquivo_interno).read()
    elif formato_compactado == 'tar.gz':
        with tarfile.open(fileobj=arquivo_bytes, mode='r:gz') as t:
            if isinstance(nome_arquivo_interno, list):
            #dupla descompactação: TAR.GZ dentro de TAR.GZ
            #extrai o TAR.GZ intermediário
                conteudo_intermediario = io.BytesIO(t.extractfile(nome_arquivo_interno[0]).read())
            #abre o TAR.GZ intermediário e extrair o CSV final
                with tarfile.open(fileobj=conteudo_intermediario, mode='r:gz') as t2:
                    conteudo = t2.extractfile(nome_arquivo_interno[1]).read()
            else:
            #descompactação simples: TAR.GZ com CSV direto
                conteudo = t.extractfile(nome_arquivo_interno).read()

    #lendo o arquivo com o Polars
    df = pl.read_csv(conteudo, separator=separador, encoding=encoding, infer_schema_length=0)
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
    caminho_particao = f'{destino_bronze}/bronze_raw/{sistema}/year={ano}/month={mes}'
    
    #verificação de idempotência (se Raw já existe - pula)
    if caminho_particao.startswith("gs://"):
        fs = gcsfs.GCSFileSystem()
        if fs.exists(f'{caminho_particao}/part-000.parquet'):
            logging.info(f'Raw já existe para {sistema} {ano}/{mes}. Pulando download')
            return

    #verificando caminho
    if not caminho_particao.startswith("gs://"):
        #criando diretorio
        os.makedirs(caminho_particao, exist_ok=True)
    
    #salvando o arquivo
    df.write_parquet(f'{caminho_particao}/part-000.parquet')
    logging.info('Arquivo salvo com sucesso!')

#função auxiliar para garantir snake_case
def para_snake_case(texto):
    """Converte nome de coluna para snake_case."""
    texto = str(texto).strip().lower()
    texto = re.sub(r'[^\w\s-]', '', texto)
    texto = re.sub(r'[\s-]+', '_', texto)
    return texto

#função para normalização das bases
def normalizacao_da_bronze_raw(sistema, ano, mes):
    """Lê Parquet da Bronze Raw, padroniza colunas e salva na Bronze Normalized."""

    #definindo local de leitura dos dados
    caminho_origem = f'{destino_bronze}/bronze_raw/{sistema}/year={ano}/month={mes}/part-000.parquet'

    #verificando existência do arquivo no GCS
    if caminho_origem.startswith("gs://"):
        fs = gcsfs.GCSFileSystem()
        if not fs.exists(caminho_origem):
            logging.info(f"A partição {ano}/{mes} do sistema {sistema} não existe!")
            return
    else:
        if not os.path.exists(caminho_origem):
            logging.error(f"Arquivo não encontrado na origem: {caminho_origem}")
            return

    #estabelecendo pasta de destino bronze_normalized
    caminho_destino_pasta = f'{destino_bronze}/bronze_normalized/{sistema}/year={ano}/month={mes}'

    #verificação de idempotência (se já existe - pula)
    if caminho_destino_pasta.startswith("gs://"):
        fs = gcsfs.GCSFileSystem()
        if fs.exists(f'{caminho_destino_pasta}/part-000.parquet'):
            logging.info(f'Normalize já existe para {sistema} {ano}/{mes}. Pulando.')
            return

    # lendo arquivo parquet
    df_normalizado = pl.read_parquet(caminho_origem)
    logging.info(f'Lendo arquivo na origem: {sistema} ({ano}/{mes})')

    # Transformação do nome das colunas - snake_case
    mapeamento_colunas = {coluna: para_snake_case(coluna) for coluna in df_normalizado.columns}
    df_normalizado = df_normalizado.rename(mapeamento_colunas)
    logging.info('Colunas transformadas para snake_case com sucesso!')

    # Injeção de Metadados Universais (Arquitetura Fase 0)
    df_normalizado = df_normalizado.with_columns([
        pl.lit(sistema).alias('source_system'),
        pl.lit(datetime.now()).alias('ingestion_timestamp'),
        pl.lit('v1').alias('schema_version')
    ])
    logging.info('Metadados universais (source_system, ingestion_timestamp, schema_version) injetados!')

    #verificando caminho
    if not caminho_destino_pasta.startswith("gs://"):
        # criando diretorio
        os.makedirs(caminho_destino_pasta, exist_ok=True)
    
    # salvando o arquivo
    df_normalizado.write_parquet(f'{caminho_destino_pasta}/part-000.parquet')
    logging.info(f'Arquivo salvo com sucesso em: {caminho_destino_pasta}')